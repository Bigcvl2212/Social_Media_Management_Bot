"""
Growth Tracker — tracks follower count, engagement rate, reach, impressions
over time. Generates milestone posts. Produces weekly reports.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_DATA_DIR = Path(settings.UPLOAD_DIR) / "growth_data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_INDEX_PATH = _DATA_DIR / "growth_index.json"


class GrowthTrackerService:
    """Tracks social media growth metrics and generates reports."""

    def __init__(self):
        self._data = self._load_data()

    # ════════════════════════════════════════════════════════════════
    #  PERSISTENCE
    # ════════════════════════════════════════════════════════════════

    def _load_data(self) -> Dict[str, Any]:
        if _INDEX_PATH.exists():
            try:
                return json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
            except Exception:
                logger.warning("Corrupt growth data, starting fresh")
        return {
            "snapshots": [],  # daily metric snapshots
            "milestones": [],  # achieved milestones
            "milestone_targets": [100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
            "goals": {
                "weekly_follower_growth": 50,
                "weekly_posts": 20,
                "engagement_rate_target": 3.0,
            },
            "weekly_reports": [],
        }

    def _save_data(self) -> None:
        _INDEX_PATH.write_text(
            json.dumps(self._data, indent=2, default=str),
            encoding="utf-8",
        )

    # ════════════════════════════════════════════════════════════════
    #  RECORD SNAPSHOT — called daily by scheduler or manually
    # ════════════════════════════════════════════════════════════════

    def record_snapshot(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Record a daily metrics snapshot.

        metrics: {followers, likes, reach, impressions, posts_count,
                  engagement_rate, top_post_id, top_post_engagement}
        """
        snapshot = {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "timestamp": datetime.utcnow().isoformat(),
            "followers": metrics.get("followers", 0),
            "page_likes": metrics.get("likes", 0),
            "reach": metrics.get("reach", 0),
            "impressions": metrics.get("impressions", 0),
            "posts_count": metrics.get("posts_count", 0),
            "engagement_rate": metrics.get("engagement_rate", 0),
            "top_post_id": metrics.get("top_post_id", ""),
            "top_post_engagement": metrics.get("top_post_engagement", 0),
        }

        # Prevent duplicate snapshots on same day
        today = snapshot["date"]
        existing_idx = next(
            (i for i, s in enumerate(self._data["snapshots"]) if s["date"] == today),
            None,
        )
        if existing_idx is not None:
            self._data["snapshots"][existing_idx] = snapshot
        else:
            self._data["snapshots"].append(snapshot)

        # Check milestones
        new_milestones = self._check_milestones(snapshot["followers"])

        # Keep last 365 days of snapshots
        if len(self._data["snapshots"]) > 365:
            self._data["snapshots"] = self._data["snapshots"][-365:]

        self._save_data()

        return {
            "snapshot": snapshot,
            "new_milestones": new_milestones,
        }

    def _check_milestones(self, followers: int) -> List[Dict[str, Any]]:
        """Check if any milestone targets have been hit."""
        new = []
        achieved_values = {m["value"] for m in self._data["milestones"]}
        for target in self._data.get("milestone_targets", []):
            if followers >= target and target not in achieved_values:
                milestone = {
                    "value": target,
                    "achieved_at": datetime.utcnow().isoformat(),
                    "followers_at_time": followers,
                    "celebration_post": self._milestone_caption(target),
                }
                self._data["milestones"].append(milestone)
                new.append(milestone)
        return new

    @staticmethod
    def _milestone_caption(target: int) -> str:
        """Generate a celebration caption for hitting a milestone."""
        captions = {
            100: "We just hit 100 followers! 🎉 Small but mighty — this journey is just getting started! Thank you for being here! 💪",
            250: "250 strong! 💪 This community keeps growing and we're loving every minute of it. Thank you ALL! 🔥",
            500: "500 FOLLOWERS! 🎉🔥 Half a thousand people believe in what we're building. You guys are incredible! 💪",
            1000: "🚨 1,000 FOLLOWERS! 🚨 We did it! This milestone means everything. Thank you for being part of this journey! 🎉💪🔥",
            2500: "2,500! 🤯 This community is GROWING. Every single one of you makes this page what it is. LET'S GO! 🔥💪",
            5000: "5K STRONG! 💪🔥 Five thousand people. We're building something special here and the best is yet to come! 🎉",
            10000: "10,000 FOLLOWERS! 🎉🔥💪 TEN THOUSAND! This is unreal. Thank you for making this happen. We're just getting started! 🚀",
            25000: "25K! 🤯🔥 Twenty-five THOUSAND of you! This community is EVERYTHING. Big things coming! 💪🎉",
            50000: "50,000 FOLLOWERS! 🚀 FIFTY THOUSAND! What started as a dream is now a movement. Thank you! 🔥💪🎉",
            100000: "100K! 🎉🔥💪🚀 ONE HUNDRED THOUSAND! WE MADE IT! This is YOUR achievement. Every single one of you. THANK YOU! 🎊",
        }
        return captions.get(target, f"We just hit {target:,} followers! 🎉 Thank you all! 💪🔥")

    # ════════════════════════════════════════════════════════════════
    #  REPORTS
    # ════════════════════════════════════════════════════════════════

    def get_weekly_report(self) -> Dict[str, Any]:
        """Generate a report for the last 7 days."""
        snapshots = self._data["snapshots"]
        if not snapshots:
            return {"error": "No data yet. Record daily snapshots first."}

        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)

        this_week = [s for s in snapshots if s["date"] >= week_ago.strftime("%Y-%m-%d")]
        last_week = [s for s in snapshots
                     if two_weeks_ago.strftime("%Y-%m-%d") <= s["date"] < week_ago.strftime("%Y-%m-%d")]

        if not this_week:
            return {"error": "No snapshots this week."}

        latest = this_week[-1]
        earliest = this_week[0]

        follower_growth = latest["followers"] - earliest["followers"]
        avg_engagement = sum(s.get("engagement_rate", 0) for s in this_week) / len(this_week)
        total_reach = sum(s.get("reach", 0) for s in this_week)
        total_impressions = sum(s.get("impressions", 0) for s in this_week)
        total_posts = sum(s.get("posts_count", 0) for s in this_week)

        # Week-over-week comparison
        wow = {}
        if last_week:
            prev_latest = last_week[-1]
            prev_earliest = last_week[0]
            prev_growth = prev_latest["followers"] - prev_earliest["followers"]
            wow["follower_growth_change"] = follower_growth - prev_growth
            prev_avg_engagement = sum(s.get("engagement_rate", 0) for s in last_week) / len(last_week)
            wow["engagement_change"] = round(avg_engagement - prev_avg_engagement, 2)
            prev_reach = sum(s.get("reach", 0) for s in last_week)
            wow["reach_change_pct"] = round(((total_reach - prev_reach) / max(prev_reach, 1)) * 100, 1)

        goals = self._data.get("goals", {})
        report = {
            "period": f"{earliest['date']} to {latest['date']}",
            "current_followers": latest["followers"],
            "follower_growth": follower_growth,
            "avg_engagement_rate": round(avg_engagement, 2),
            "total_reach": total_reach,
            "total_impressions": total_impressions,
            "total_posts": total_posts,
            "best_day": max(this_week, key=lambda s: s.get("engagement_rate", 0))["date"] if this_week else None,
            "week_over_week": wow,
            "goals": {
                "follower_growth": {
                    "target": goals.get("weekly_follower_growth", 50),
                    "actual": follower_growth,
                    "met": follower_growth >= goals.get("weekly_follower_growth", 50),
                },
                "posts": {
                    "target": goals.get("weekly_posts", 20),
                    "actual": total_posts,
                    "met": total_posts >= goals.get("weekly_posts", 20),
                },
                "engagement": {
                    "target": goals.get("engagement_rate_target", 3.0),
                    "actual": round(avg_engagement, 2),
                    "met": avg_engagement >= goals.get("engagement_rate_target", 3.0),
                },
            },
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Store report
        self._data["weekly_reports"].append(report)
        if len(self._data["weekly_reports"]) > 52:
            self._data["weekly_reports"] = self._data["weekly_reports"][-52:]
        self._save_data()

        return report

    def get_trend_data(self, days: int = 30) -> Dict[str, Any]:
        """Return metrics for charting (last N days)."""
        cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
        snapshots = [s for s in self._data["snapshots"] if s["date"] >= cutoff]
        return {
            "dates": [s["date"] for s in snapshots],
            "followers": [s["followers"] for s in snapshots],
            "engagement_rates": [s.get("engagement_rate", 0) for s in snapshots],
            "reach": [s.get("reach", 0) for s in snapshots],
            "impressions": [s.get("impressions", 0) for s in snapshots],
            "posts": [s.get("posts_count", 0) for s in snapshots],
        }

    # ════════════════════════════════════════════════════════════════
    #  GOALS / MILESTONES / DASHBOARD
    # ════════════════════════════════════════════════════════════════

    def update_goals(self, goals: Dict[str, Any]) -> Dict[str, Any]:
        g = self._data.setdefault("goals", {})
        for key in ("weekly_follower_growth", "weekly_posts", "engagement_rate_target"):
            if key in goals:
                g[key] = goals[key]
        self._save_data()
        return g

    def get_goals(self) -> Dict[str, Any]:
        return self._data.get("goals", {})

    def get_milestones(self) -> List[Dict[str, Any]]:
        return self._data["milestones"]

    def get_dashboard(self) -> Dict[str, Any]:
        """Full dashboard data bundle."""
        snapshots = self._data["snapshots"]
        latest = snapshots[-1] if snapshots else {}
        prev = snapshots[-2] if len(snapshots) >= 2 else {}

        return {
            "current": latest,
            "previous": prev,
            "follower_change": latest.get("followers", 0) - prev.get("followers", 0) if prev else 0,
            "milestones": self._data["milestones"],
            "goals": self._data.get("goals", {}),
            "total_snapshots": len(snapshots),
            "trend_7d": self.get_trend_data(7),
            "trend_30d": self.get_trend_data(30),
        }

    def get_all_snapshots(self, limit: int = 30) -> List[Dict[str, Any]]:
        return self._data["snapshots"][-limit:]
