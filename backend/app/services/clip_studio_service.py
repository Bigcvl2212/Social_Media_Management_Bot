"""
Clip Studio Service — Raw footage → viral clips using ffmpeg + Gemini AI.

Flow:
  1. Upload raw footage → save to uploads/raw_footage/
  2. Analyze with ffprobe (metadata) + ffmpeg (scene detect) + Gemini (AI scene scoring)
  3. User selects clips → ffmpeg extracts, crops to aspect ratio, optional captions
  4. Generated clips saved to uploads/generated/clips/
"""

import asyncio
import json
import logging
import os
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Directories ──────────────────────────────────────────────────
_UPLOAD_BASE = Path(settings.UPLOAD_DIR)
RAW_FOOTAGE_DIR = _UPLOAD_BASE / "raw_footage"
CLIPS_DIR = _UPLOAD_BASE / "generated" / "clips"
THUMBS_DIR = _UPLOAD_BASE / "generated" / "thumbnails"
METADATA_DIR = _UPLOAD_BASE / "clip_studio_data"

for _d in (RAW_FOOTAGE_DIR, CLIPS_DIR, THUMBS_DIR, METADATA_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ── Aspect ratio presets ─────────────────────────────────────────
ASPECT_PRESETS = {
    "9:16": {"w": 1080, "h": 1920, "label": "TikTok / Reels / Shorts"},
    "16:9": {"w": 1920, "h": 1080, "label": "YouTube / Facebook"},
    "1:1":  {"w": 1080, "h": 1080, "label": "Instagram Feed"},
    "4:5":  {"w": 1080, "h": 1350, "label": "Instagram Portrait"},
}


class ClipStudioService:
    """Turns raw footage into platform-ready viral clips."""

    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        self._client = genai.Client(api_key=api_key)
        self._footage_index = self._load_index()

    # ════════════════════════════════════════════════════════════════
    #  INDEX PERSISTENCE (JSON file — no DB migration needed)
    # ════════════════════════════════════════════════════════════════

    def _index_path(self) -> Path:
        return METADATA_DIR / "footage_index.json"

    def _load_index(self) -> Dict[str, Any]:
        p = self._index_path()
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                logger.warning("Corrupt footage index, starting fresh")
        return {}

    def _save_index(self) -> None:
        self._index_path().write_text(
            json.dumps(self._footage_index, indent=2, default=str),
            encoding="utf-8",
        )

    # ════════════════════════════════════════════════════════════════
    #  UPLOAD
    # ════════════════════════════════════════════════════════════════

    async def save_upload(self, filename: str, data: bytes) -> Dict[str, Any]:
        """Save an uploaded video file and extract basic metadata."""
        footage_id = uuid.uuid4().hex[:12]
        safe_name = f"{footage_id}_{filename}"
        dest = RAW_FOOTAGE_DIR / safe_name
        dest.write_bytes(data)

        meta = await self._ffprobe_metadata(str(dest))

        # Generate thumbnail
        thumb_name = f"{footage_id}_thumb.jpg"
        thumb_path = THUMBS_DIR / thumb_name
        await self._extract_thumbnail(str(dest), str(thumb_path), seek=min(2.0, meta.get("duration", 0) / 3))

        record = {
            "id": footage_id,
            "filename": filename,
            "safe_name": safe_name,
            "path": str(dest),
            "thumbnail": thumb_name,
            "duration": meta.get("duration", 0),
            "width": meta.get("width", 0),
            "height": meta.get("height", 0),
            "fps": meta.get("fps", 30),
            "codec": meta.get("codec", "unknown"),
            "size_bytes": len(data),
            "uploaded_at": datetime.utcnow().isoformat(),
            "analysis": None,
            "clips": [],
        }
        self._footage_index[footage_id] = record
        self._save_index()

        return record

    # ════════════════════════════════════════════════════════════════
    #  LIST / GET / DELETE
    # ════════════════════════════════════════════════════════════════

    def list_footage(self) -> List[Dict[str, Any]]:
        items = sorted(self._footage_index.values(), key=lambda x: x.get("uploaded_at", ""), reverse=True)
        return [self._footage_summary(f) for f in items]

    def get_footage(self, footage_id: str) -> Optional[Dict[str, Any]]:
        return self._footage_index.get(footage_id)

    def delete_footage(self, footage_id: str) -> bool:
        rec = self._footage_index.pop(footage_id, None)
        if not rec:
            return False
        # Clean up files
        for p in (Path(rec["path"]), THUMBS_DIR / rec.get("thumbnail", "")):
            if p.exists():
                p.unlink(missing_ok=True)
        # Clean up clips
        for clip in rec.get("clips", []):
            cp = Path(clip.get("path", ""))
            if cp.exists():
                cp.unlink(missing_ok=True)
        self._save_index()
        return True

    def _footage_summary(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Return a lightweight summary for the list view."""
        return {
            "id": rec["id"],
            "filename": rec["filename"],
            "thumbnail": rec.get("thumbnail"),
            "duration": rec["duration"],
            "width": rec.get("width", 0),
            "height": rec.get("height", 0),
            "size_bytes": rec.get("size_bytes", 0),
            "uploaded_at": rec["uploaded_at"],
            "analyzed": rec.get("analysis") is not None,
            "clip_count": len(rec.get("clips", [])),
        }

    # ════════════════════════════════════════════════════════════════
    #  ANALYZE — ffmpeg scene detect + Gemini AI scoring
    # ════════════════════════════════════════════════════════════════

    async def analyze_footage(self, footage_id: str) -> Dict[str, Any]:
        """Run AI-powered analysis on uploaded footage."""
        rec = self._footage_index.get(footage_id)
        if not rec:
            raise ValueError(f"Footage {footage_id} not found")

        video_path = rec["path"]
        duration = rec["duration"]

        # 1. Scene detection with ffmpeg
        scenes = await self._detect_scenes(video_path, duration)

        # 2. Extract keyframes for AI analysis (1 per scene, max 20)
        keyframe_paths = await self._extract_keyframes(video_path, scenes)

        # 3. Send keyframes + metadata to Gemini for smart analysis
        ai_analysis = await self._gemini_analyze_scenes(
            scenes, keyframe_paths, duration, rec["filename"]
        )

        # 4. Merge AI suggestions into scene data
        analysis = {
            "total_scenes": len(scenes),
            "scenes": ai_analysis,
            "analyzed_at": datetime.utcnow().isoformat(),
            "recommended_clips": [s for s in ai_analysis if s.get("viral_score", 0) >= 7],
        }

        rec["analysis"] = analysis
        self._save_index()

        # Cleanup temp keyframes
        for kp in keyframe_paths:
            Path(kp).unlink(missing_ok=True)

        return analysis

    # ════════════════════════════════════════════════════════════════
    #  GENERATE CLIPS — cut + crop + optional captions
    # ════════════════════════════════════════════════════════════════

    async def generate_clips(
        self,
        footage_id: str,
        clip_selections: List[Dict[str, Any]],
        aspect_ratio: str = "9:16",
        add_captions: bool = False,
    ) -> List[Dict[str, Any]]:
        """Generate clips from selected scenes.

        clip_selections: list of {scene_index, start, end, title}
        """
        rec = self._footage_index.get(footage_id)
        if not rec:
            raise ValueError(f"Footage {footage_id} not found")

        video_path = rec["path"]
        preset = ASPECT_PRESETS.get(aspect_ratio, ASPECT_PRESETS["9:16"])
        generated = []

        for sel in clip_selections:
            clip_id = uuid.uuid4().hex[:8]
            start = float(sel["start"])
            end = float(sel["end"])
            title = sel.get("title", f"Clip {sel.get('scene_index', '?')}")
            clip_filename = f"{footage_id}_{clip_id}.mp4"
            clip_path = CLIPS_DIR / clip_filename

            # ffmpeg: cut + scale + crop to aspect ratio
            await self._ffmpeg_extract_clip(
                video_path, str(clip_path), start, end,
                preset["w"], preset["h"]
            )

            # Thumbnail for this clip
            clip_thumb = f"{footage_id}_{clip_id}_thumb.jpg"
            await self._extract_thumbnail(str(clip_path), str(THUMBS_DIR / clip_thumb))

            clip_dur = end - start
            clip_rec = {
                "clip_id": clip_id,
                "footage_id": footage_id,
                "filename": clip_filename,
                "path": str(clip_path),
                "thumbnail": clip_thumb,
                "start": start,
                "end": end,
                "duration": round(clip_dur, 2),
                "title": title,
                "aspect_ratio": aspect_ratio,
                "resolution": f"{preset['w']}x{preset['h']}",
                "created_at": datetime.utcnow().isoformat(),
            }
            rec.setdefault("clips", []).append(clip_rec)
            generated.append(clip_rec)

        self._save_index()
        return generated

    def list_clips(self, footage_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all generated clips, optionally filtered by footage."""
        clips = []
        for rec in self._footage_index.values():
            for c in rec.get("clips", []):
                if footage_id is None or c.get("footage_id") == footage_id:
                    clips.append(c)
        clips.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return clips

    def delete_clip(self, clip_id: str) -> bool:
        for rec in self._footage_index.values():
            for i, c in enumerate(rec.get("clips", [])):
                if c["clip_id"] == clip_id:
                    path = Path(c.get("path", ""))
                    if path.exists():
                        path.unlink(missing_ok=True)
                    thumb = THUMBS_DIR / c.get("thumbnail", "")
                    if thumb.exists():
                        thumb.unlink(missing_ok=True)
                    rec["clips"].pop(i)
                    self._save_index()
                    return True
        return False

    # ════════════════════════════════════════════════════════════════
    #  PRIVATE — ffprobe / ffmpeg helpers
    # ════════════════════════════════════════════════════════════════

    async def _ffprobe_metadata(self, path: str) -> Dict[str, Any]:
        proc = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "error", "-show_format", "-show_streams",
            "-print_format", "json", path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        data = json.loads(stdout.decode())
        fmt = data.get("format", {})
        vs = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
        fps_str = vs.get("r_frame_rate", "30/1")
        try:
            num, den = fps_str.split("/")
            fps = round(float(num) / float(den), 2)
        except Exception:
            fps = 30.0
        return {
            "duration": float(fmt.get("duration", 0)),
            "width": int(vs.get("width", 0)),
            "height": int(vs.get("height", 0)),
            "fps": fps,
            "codec": vs.get("codec_name", "unknown"),
        }

    async def _detect_scenes(self, path: str, duration: float) -> List[Dict[str, Any]]:
        """Use ffmpeg scene-change detection filter."""
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", path,
            "-filter:v", "select='gt(scene,0.35)',showinfo",
            "-f", "null", "-",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        output = stderr.decode(errors="replace")

        scene_times = [0.0]
        for line in output.split("\n"):
            if "pts_time:" in line:
                try:
                    pts = float(line.split("pts_time:")[1].split()[0])
                    if pts - scene_times[-1] > 1.5:  # min 1.5s between scenes
                        scene_times.append(pts)
                except (ValueError, IndexError):
                    pass
        scene_times.append(duration)

        scenes = []
        for i in range(len(scene_times) - 1):
            s, e = scene_times[i], scene_times[i + 1]
            if e - s >= 1.0:  # skip sub-1s fragments
                scenes.append({
                    "index": i,
                    "start": round(s, 2),
                    "end": round(e, 2),
                    "duration": round(e - s, 2),
                })
        return scenes

    async def _extract_keyframes(self, path: str, scenes: List[Dict]) -> List[str]:
        """Extract one representative frame per scene (mid-point)."""
        paths = []
        for scene in scenes[:20]:  # cap at 20 frames for API cost
            mid = (scene["start"] + scene["end"]) / 2
            out = str(METADATA_DIR / f"_kf_{scene['index']}.jpg")
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg", "-y", "-ss", str(mid), "-i", path,
                "-frames:v", "1", "-q:v", "3", out,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            await proc.communicate()
            if Path(out).exists():
                paths.append(out)
        return paths

    async def _extract_thumbnail(self, video_path: str, out_path: str, seek: float = 1.0) -> None:
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-ss", str(seek), "-i", video_path,
            "-frames:v", "1", "-q:v", "4", out_path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()

    async def _ffmpeg_extract_clip(
        self, src: str, dst: str, start: float, end: float, w: int, h: int
    ) -> None:
        """Cut a segment and smart-crop to target resolution."""
        dur = end - start
        # Smart crop: scale to cover target, then center-crop
        vf = (
            f"scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},"
            f"setsar=1"
        )
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start), "-i", src, "-t", str(dur),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            dst,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"ffmpeg clip extraction failed: {stderr.decode()[-500:]}")

    # ════════════════════════════════════════════════════════════════
    #  PRIVATE — Gemini AI analysis
    # ════════════════════════════════════════════════════════════════

    async def _gemini_analyze_scenes(
        self,
        scenes: List[Dict],
        keyframe_paths: List[str],
        total_duration: float,
        filename: str,
    ) -> List[Dict[str, Any]]:
        """Send keyframes to Gemini for viral-potential scoring."""

        prompt = f"""You are a professional viral content editor for social media (TikTok, Instagram Reels, YouTube Shorts).

I'm giving you {len(keyframe_paths)} keyframes from a raw video ({total_duration:.0f}s long, file: {filename}).
Each keyframe represents a scene. Analyze each scene and rate its viral potential.

For each scene, return a JSON array where each element has:
- "scene_index": integer (0-based, matching the order of images)
- "title": short catchy clip title (3-8 words)
- "description": what's happening in this scene (1 sentence)
- "viral_score": 1-10 (10 = extremely viral, hook-worthy)
- "energy": "low" | "medium" | "high"
- "best_as": "hook" | "highlight" | "outro" | "b-roll"
- "reason": why this would or wouldn't work as a viral clip (1 sentence)
- "suggested_caption": a short social media caption if this were posted

Return ONLY the JSON array, no markdown fences."""

        # Build content parts: text prompt + images
        parts = [prompt]
        for kf_path in keyframe_paths:
            try:
                img_bytes = Path(kf_path).read_bytes()
                parts.append(types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"))
            except Exception as e:
                logger.warning(f"Failed to read keyframe {kf_path}: {e}")

        try:
            response = await asyncio.to_thread(
                self._client.models.generate_content,
                model="gemini-2.5-flash-lite",
                contents=parts,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                ),
            )
            raw_text = response.text or ""
            ai_scenes = self._extract_json(raw_text)
            if not isinstance(ai_scenes, list):
                ai_scenes = []
        except Exception as e:
            logger.error(f"Gemini scene analysis failed: {e}")
            ai_scenes = []

        # Merge AI results with ffmpeg scene data
        result = []
        for scene in scenes:
            idx = scene["index"]
            ai = next((a for a in ai_scenes if a.get("scene_index") == idx), {})
            result.append({
                **scene,
                "title": ai.get("title", f"Scene {idx + 1}"),
                "description": ai.get("description", ""),
                "viral_score": ai.get("viral_score", 5),
                "energy": ai.get("energy", "medium"),
                "best_as": ai.get("best_as", "b-roll"),
                "reason": ai.get("reason", ""),
                "suggested_caption": ai.get("suggested_caption", ""),
            })
        return result

    @staticmethod
    def _extract_json(text: str):
        """Extract JSON from LLM output, stripping markdown fences."""
        import re
        text = text.strip()
        m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if m:
            text = m.group(1).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find array in text
            start = text.find("[")
            end = text.rfind("]")
            if start != -1 and end != -1:
                try:
                    return json.loads(text[start:end + 1])
                except json.JSONDecodeError:
                    pass
        return None
