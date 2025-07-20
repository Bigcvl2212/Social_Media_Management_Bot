"""
Accessibility checking service for social media content
Provides comprehensive accessibility analysis for posts, images, and videos
"""

from typing import Dict, List, Optional, Any, Tuple
import re
import colorsys
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from pathlib import Path
import textstat
try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
import magic
import asyncio
from dataclasses import dataclass
from enum import Enum


class AccessibilityLevel(Enum):
    """Accessibility compliance levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"


@dataclass
class AccessibilityIssue:
    """Represents an accessibility issue"""
    type: str
    severity: str
    message: str
    suggestion: str
    wcag_guideline: Optional[str] = None


@dataclass
class AccessibilityScore:
    """Accessibility score with breakdown"""
    overall_score: float
    level: AccessibilityLevel
    alt_text_score: float
    contrast_score: float
    text_readability_score: float
    subtitle_score: float
    issues: List[AccessibilityIssue]


class AccessibilityService:
    """Service for accessibility analysis and checking"""
    
    def __init__(self):
        self.min_contrast_ratio = 4.5  # WCAG AA standard
        self.min_large_text_contrast = 3.0  # WCAG AA for large text
        self.max_readability_grade = 8  # 8th grade reading level
        
    async def analyze_content_accessibility(
        self, 
        content_data: Dict[str, Any],
        media_files: Optional[List[str]] = None
    ) -> AccessibilityScore:
        """
        Comprehensive accessibility analysis for social media content
        
        Args:
            content_data: Content information (text, caption, etc.)
            media_files: List of media file paths
            
        Returns:
            AccessibilityScore with detailed analysis
        """
        issues = []
        scores = {
            'alt_text': 0.0,
            'contrast': 0.0,
            'readability': 0.0,
            'subtitle': 0.0
        }
        
        # Analyze text content
        text_content = content_data.get('caption', '') + ' ' + content_data.get('title', '')
        if text_content.strip():
            readability_score, readability_issues = await self._analyze_text_readability(text_content)
            scores['readability'] = readability_score
            issues.extend(readability_issues)
        
        # Analyze media files
        if media_files:
            for file_path in media_files:
                try:
                    file_type = self._get_file_type(file_path)
                    
                    if file_type.startswith('image/'):
                        alt_score, alt_issues = await self._analyze_image_accessibility(
                            file_path, content_data.get('alt_text', '')
                        )
                        contrast_score, contrast_issues = await self._analyze_image_contrast(file_path)
                        
                        scores['alt_text'] = max(scores['alt_text'], alt_score)
                        scores['contrast'] = max(scores['contrast'], contrast_score)
                        issues.extend(alt_issues)
                        issues.extend(contrast_issues)
                        
                    elif file_type.startswith('video/'):
                        subtitle_score, subtitle_issues = await self._analyze_video_accessibility(
                            file_path, content_data.get('subtitles', '')
                        )
                        scores['subtitle'] = max(scores['subtitle'], subtitle_score)
                        issues.extend(subtitle_issues)
                        
                except Exception as e:
                    issues.append(AccessibilityIssue(
                        type="file_analysis",
                        severity="warning",
                        message=f"Could not analyze file {file_path}: {str(e)}",
                        suggestion="Ensure file is accessible and in supported format"
                    ))
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(scores)
        level = self._determine_accessibility_level(overall_score)
        
        return AccessibilityScore(
            overall_score=overall_score,
            level=level,
            alt_text_score=scores['alt_text'],
            contrast_score=scores['contrast'],
            text_readability_score=scores['readability'],
            subtitle_score=scores['subtitle'],
            issues=issues
        )
    
    async def _analyze_text_readability(self, text: str) -> Tuple[float, List[AccessibilityIssue]]:
        """Analyze text readability and complexity"""
        issues = []
        score = 100.0
        
        try:
            # Reading level analysis
            flesch_score = textstat.flesch_reading_ease(text)
            grade_level = textstat.flesch_kincaid_grade(text)
            
            if grade_level > self.max_readability_grade:
                issues.append(AccessibilityIssue(
                    type="readability",
                    severity="warning",
                    message=f"Text reading level is grade {grade_level:.1f} (target: {self.max_readability_grade})",
                    suggestion="Consider simplifying language and sentence structure",
                    wcag_guideline="3.1.5"
                ))
                score -= 20
            
            # Check for overly complex sentences
            sentences = re.split(r'[.!?]+', text)
            long_sentences = [s for s in sentences if len(s.split()) > 20]
            if long_sentences:
                issues.append(AccessibilityIssue(
                    type="readability",
                    severity="info",
                    message=f"Found {len(long_sentences)} sentences with >20 words",
                    suggestion="Consider breaking long sentences into shorter ones"
                ))
                score -= 10
            
            # Check for proper punctuation
            if not re.search(r'[.!?]$', text.strip()):
                issues.append(AccessibilityIssue(
                    type="readability",
                    severity="info",
                    message="Text lacks proper ending punctuation",
                    suggestion="Add appropriate punctuation for better readability"
                ))
                score -= 5
                
        except Exception as e:
            issues.append(AccessibilityIssue(
                type="readability",
                severity="error",
                message=f"Could not analyze text readability: {str(e)}",
                suggestion="Check text content format"
            ))
            score = 50.0
        
        return max(0.0, score), issues
    
    async def _analyze_image_accessibility(self, image_path: str, alt_text: str) -> Tuple[float, List[AccessibilityIssue]]:
        """Analyze image accessibility including alt text"""
        issues = []
        score = 100.0
        
        # Check if alt text exists
        if not alt_text or not alt_text.strip():
            issues.append(AccessibilityIssue(
                type="alt_text",
                severity="error",
                message="Missing alt text for image",
                suggestion="Add descriptive alt text that conveys the image's purpose and content",
                wcag_guideline="1.1.1"
            ))
            score = 0.0
        else:
            # Analyze alt text quality
            alt_words = alt_text.split()
            
            if len(alt_words) < 3:
                issues.append(AccessibilityIssue(
                    type="alt_text",
                    severity="warning",
                    message="Alt text is very short",
                    suggestion="Provide more descriptive alt text (aim for 5-15 words)",
                    wcag_guideline="1.1.1"
                ))
                score -= 30
            
            if len(alt_words) > 50:
                issues.append(AccessibilityIssue(
                    type="alt_text",
                    severity="warning",
                    message="Alt text is very long",
                    suggestion="Keep alt text concise while being descriptive",
                    wcag_guideline="1.1.1"
                ))
                score -= 20
            
            # Check for redundant phrases
            redundant_phrases = ['image of', 'picture of', 'photo of', 'graphic of']
            alt_lower = alt_text.lower()
            for phrase in redundant_phrases:
                if phrase in alt_lower:
                    issues.append(AccessibilityIssue(
                        type="alt_text",
                        severity="info",
                        message=f"Alt text contains redundant phrase: '{phrase}'",
                        suggestion="Remove redundant phrases like 'image of' from alt text"
                    ))
                    score -= 10
                    break
        
        return max(0.0, score), issues
    
    async def _analyze_image_contrast(self, image_path: str) -> Tuple[float, List[AccessibilityIssue]]:
        """Analyze color contrast in images"""
        issues = []
        score = 100.0
        
        try:
            # Load image
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Sample colors from image
            width, height = image.size
            sample_points = []
            
            # Sample from different regions
            for y in range(0, height, height // 10):
                for x in range(0, width, width // 10):
                    if x < width and y < height:
                        sample_points.append((x, y))
            
            # Calculate contrast ratios
            low_contrast_count = 0
            total_samples = len(sample_points)
            
            if total_samples > 1:
                for i in range(0, len(sample_points) - 1, 2):
                    x1, y1 = sample_points[i]
                    x2, y2 = sample_points[i + 1]
                    
                    color1 = image.getpixel((x1, y1))
                    color2 = image.getpixel((x2, y2))
                    
                    contrast_ratio = self._calculate_contrast_ratio(color1, color2)
                    
                    if contrast_ratio < self.min_contrast_ratio:
                        low_contrast_count += 1
                
                low_contrast_percentage = (low_contrast_count / (total_samples // 2)) * 100
                
                if low_contrast_percentage > 50:
                    issues.append(AccessibilityIssue(
                        type="contrast",
                        severity="error",
                        message=f"Poor color contrast detected in {low_contrast_percentage:.1f}% of sampled areas",
                        suggestion="Increase contrast between text and background colors",
                        wcag_guideline="1.4.3"
                    ))
                    score = 20.0
                elif low_contrast_percentage > 25:
                    issues.append(AccessibilityIssue(
                        type="contrast",
                        severity="warning",
                        message=f"Low color contrast in {low_contrast_percentage:.1f}% of sampled areas",
                        suggestion="Consider improving contrast for better accessibility",
                        wcag_guideline="1.4.3"
                    ))
                    score = 60.0
                    
        except Exception as e:
            issues.append(AccessibilityIssue(
                type="contrast",
                severity="error",
                message=f"Could not analyze image contrast: {str(e)}",
                suggestion="Ensure image file is accessible and in supported format"
            ))
            score = 50.0
        
        return score, issues
    
    async def _analyze_video_accessibility(self, video_path: str, subtitles: str) -> Tuple[float, List[AccessibilityIssue]]:
        """Analyze video accessibility including subtitles"""
        issues = []
        score = 100.0
        
        # Check for subtitles/captions
        if not subtitles or not subtitles.strip():
            issues.append(AccessibilityIssue(
                type="subtitles",
                severity="error",
                message="Missing subtitles/captions for video content",
                suggestion="Add accurate subtitles or captions for all audio content",
                wcag_guideline="1.2.2"
            ))
            score = 0.0
        else:
            # Analyze subtitle quality
            subtitle_words = subtitles.split()
            
            if len(subtitle_words) < 10:
                issues.append(AccessibilityIssue(
                    type="subtitles",
                    severity="warning",
                    message="Subtitles appear incomplete or very short",
                    suggestion="Ensure subtitles cover all spoken content in the video"
                ))
                score -= 30
        
        try:
            # Basic video analysis
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened():
                # Check video duration vs subtitle length
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                duration = frame_count / fps if fps > 0 else 0
                
                if duration > 30 and len(subtitle_words) < duration * 2:  # Rough estimate
                    issues.append(AccessibilityIssue(
                        type="subtitles",
                        severity="warning",
                        message="Subtitle length may not match video duration",
                        suggestion="Verify subtitles cover the entire video content"
                    ))
                    score -= 20
                
                cap.release()
                
        except Exception as e:
            issues.append(AccessibilityIssue(
                type="subtitles",
                severity="warning",
                message=f"Could not analyze video properties: {str(e)}",
                suggestion="Manually verify subtitle completeness"
            ))
        
        return max(0.0, score), issues
    
    def _calculate_contrast_ratio(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """Calculate WCAG contrast ratio between two colors"""
        def get_relative_luminance(color):
            """Calculate relative luminance of a color"""
            r, g, b = [c / 255.0 for c in color]
            
            # Apply gamma correction
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        l1 = get_relative_luminance(color1)
        l2 = get_relative_luminance(color2)
        
        # Ensure l1 is the lighter color
        if l1 < l2:
            l1, l2 = l2, l1
        
        return (l1 + 0.05) / (l2 + 0.05)
    
    def _get_file_type(self, file_path: str) -> str:
        """Get MIME type of file"""
        try:
            return magic.from_file(file_path, mime=True)
        except:
            # Fallback to extension-based detection
            ext = Path(file_path).suffix.lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                return 'image/jpeg'
            elif ext in ['.mp4', '.avi', '.mov', '.wmv']:
                return 'video/mp4'
            return 'application/octet-stream'
    
    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted overall accessibility score"""
        weights = {
            'alt_text': 0.3,
            'contrast': 0.3,
            'readability': 0.2,
            'subtitle': 0.2
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for category, score in scores.items():
            if score > 0:  # Only count categories with content
                total_score += score * weights[category]
                total_weight += weights[category]
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_accessibility_level(self, score: float) -> AccessibilityLevel:
        """Determine accessibility level based on score"""
        if score >= 90:
            return AccessibilityLevel.EXCELLENT
        elif score >= 75:
            return AccessibilityLevel.GOOD
        elif score >= 50:
            return AccessibilityLevel.NEEDS_IMPROVEMENT
        else:
            return AccessibilityLevel.POOR


# Convenience function for quick accessibility check
async def check_content_accessibility(
    content_data: Dict[str, Any],
    media_files: Optional[List[str]] = None
) -> AccessibilityScore:
    """
    Quick accessibility check for content
    
    Args:
        content_data: Content information
        media_files: List of media file paths
        
    Returns:
        AccessibilityScore
    """
    service = AccessibilityService()
    return await service.analyze_content_accessibility(content_data, media_files)