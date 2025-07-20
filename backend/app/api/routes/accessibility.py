"""
Accessibility API routes for content analysis and checking
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import tempfile
import os
from pathlib import Path

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.accessibility_service import AccessibilityService, AccessibilityScore, AccessibilityLevel


router = APIRouter()


# Pydantic models for request/response
class AccessibilityCheckRequest(BaseModel):
    """Request model for accessibility check"""
    title: Optional[str] = None
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    subtitles: Optional[str] = None


class AccessibilityIssueResponse(BaseModel):
    """Response model for accessibility issue"""
    type: str
    severity: str
    message: str
    suggestion: str
    wcag_guideline: Optional[str] = None


class AccessibilityScoreResponse(BaseModel):
    """Response model for accessibility score"""
    overall_score: float
    level: str
    alt_text_score: float
    contrast_score: float
    text_readability_score: float
    subtitle_score: float
    issues: List[AccessibilityIssueResponse]
    recommendations: List[str]


@router.post("/check", response_model=AccessibilityScoreResponse)
async def check_content_accessibility(
    request: AccessibilityCheckRequest,
    files: List[UploadFile] = File(default=[]),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check accessibility of content including text and media files
    
    Analyzes:
    - Text readability and complexity
    - Image alt text quality
    - Color contrast ratios
    - Video subtitle availability
    
    Returns comprehensive accessibility score and recommendations
    """
    try:
        accessibility_service = AccessibilityService()
        
        # Prepare content data
        content_data = {
            'title': request.title or '',
            'caption': request.caption or '',
            'alt_text': request.alt_text or '',
            'subtitles': request.subtitles or ''
        }
        
        # Handle uploaded files
        temp_files = []
        media_files = []
        
        try:
            for file in files:
                if file.filename:
                    # Create temporary file
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix)
                    temp_files.append(temp_file.name)
                    
                    # Write uploaded content to temp file
                    content = await file.read()
                    temp_file.write(content)
                    temp_file.close()
                    
                    media_files.append(temp_file.name)
            
            # Perform accessibility analysis
            score = await accessibility_service.analyze_content_accessibility(content_data, media_files)
            
            # Generate recommendations
            recommendations = _generate_recommendations(score)
            
            return AccessibilityScoreResponse(
                overall_score=score.overall_score,
                level=score.level.value,
                alt_text_score=score.alt_text_score,
                contrast_score=score.contrast_score,
                text_readability_score=score.text_readability_score,
                subtitle_score=score.subtitle_score,
                issues=[
                    AccessibilityIssueResponse(
                        type=issue.type,
                        severity=issue.severity,
                        message=issue.message,
                        suggestion=issue.suggestion,
                        wcag_guideline=issue.wcag_guideline
                    )
                    for issue in score.issues
                ],
                recommendations=recommendations
            )
            
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Accessibility check failed: {str(e)}")


@router.post("/analyze-text", response_model=Dict[str, Any])
async def analyze_text_accessibility(
    text: str = Form(...),
    language: Optional[str] = Form(default="en"),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze text accessibility and readability
    
    Returns:
    - Reading level analysis
    - Complexity metrics
    - Language detection
    - Improvement suggestions
    """
    try:
        accessibility_service = AccessibilityService()
        
        # Analyze text readability
        readability_score, issues = await accessibility_service._analyze_text_readability(text)
        
        return {
            "readability_score": readability_score,
            "issues": [
                {
                    "type": issue.type,
                    "severity": issue.severity,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                    "wcag_guideline": issue.wcag_guideline
                }
                for issue in issues
            ],
            "text_stats": {
                "word_count": len(text.split()),
                "character_count": len(text),
                "sentence_count": len([s for s in text.split('.') if s.strip()]),
                "estimated_reading_time": len(text.split()) / 200  # 200 words per minute
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")


@router.post("/analyze-image", response_model=Dict[str, Any])
async def analyze_image_accessibility(
    file: UploadFile = File(...),
    alt_text: Optional[str] = Form(default=""),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze image accessibility including alt text and contrast
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    temp_file = None
    try:
        accessibility_service = AccessibilityService()
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix)
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        
        # Analyze image
        alt_score, alt_issues = await accessibility_service._analyze_image_accessibility(
            temp_file.name, alt_text
        )
        contrast_score, contrast_issues = await accessibility_service._analyze_image_contrast(
            temp_file.name
        )
        
        return {
            "alt_text_score": alt_score,
            "contrast_score": contrast_score,
            "alt_text_issues": [
                {
                    "type": issue.type,
                    "severity": issue.severity,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                    "wcag_guideline": issue.wcag_guideline
                }
                for issue in alt_issues
            ],
            "contrast_issues": [
                {
                    "type": issue.type,
                    "severity": issue.severity,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                    "wcag_guideline": issue.wcag_guideline
                }
                for issue in contrast_issues
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")
    finally:
        if temp_file:
            try:
                os.unlink(temp_file.name)
            except:
                pass


@router.get("/guidelines", response_model=Dict[str, Any])
async def get_accessibility_guidelines(
    current_user: User = Depends(get_current_user)
):
    """
    Get accessibility guidelines and best practices
    """
    return {
        "wcag_guidelines": {
            "1.1.1": {
                "title": "Non-text Content",
                "description": "All non-text content has a text alternative",
                "level": "A"
            },
            "1.4.3": {
                "title": "Contrast (Minimum)",
                "description": "Text has a contrast ratio of at least 4.5:1",
                "level": "AA"
            },
            "1.2.2": {
                "title": "Captions (Prerecorded)",
                "description": "Captions are provided for all prerecorded audio content",
                "level": "A"
            },
            "3.1.5": {
                "title": "Reading Level",
                "description": "When text requires reading ability more advanced than the lower secondary education level after removal of proper names and titles, supplemental content, or a version that does not require reading ability more advanced than the lower secondary education level, is available",
                "level": "AAA"
            }
        },
        "best_practices": {
            "alt_text": [
                "Keep alt text concise but descriptive (5-15 words ideal)",
                "Avoid redundant phrases like 'image of' or 'picture of'",
                "Describe the function or purpose, not just appearance",
                "Include important text that appears in the image"
            ],
            "contrast": [
                "Ensure text contrast ratio is at least 4.5:1 for normal text",
                "Use 3:1 ratio for large text (18pt+ or 14pt+ bold)",
                "Test with various lighting conditions",
                "Consider colorblind users when choosing colors"
            ],
            "readability": [
                "Keep sentences under 20 words when possible",
                "Use simple, common words",
                "Break up long paragraphs",
                "Use bullet points and headers for structure"
            ],
            "video": [
                "Provide accurate captions for all speech",
                "Include sound effects and music descriptions",
                "Ensure captions are properly timed",
                "Consider audio descriptions for important visual elements"
            ]
        },
        "tools": {
            "contrast_checkers": [
                "WebAIM Contrast Checker",
                "Colour Contrast Analyser",
                "WAVE Web Accessibility Evaluator"
            ],
            "readability_tools": [
                "Hemingway Editor",
                "Readable.com",
                "Flesch-Kincaid Calculator"
            ]
        }
    }


def _generate_recommendations(score: AccessibilityScore) -> List[str]:
    """Generate personalized recommendations based on accessibility score"""
    recommendations = []
    
    if score.alt_text_score < 70:
        recommendations.append("Add descriptive alt text to all images")
        recommendations.append("Keep alt text concise but informative (5-15 words)")
    
    if score.contrast_score < 70:
        recommendations.append("Improve color contrast between text and background")
        recommendations.append("Use a contrast ratio of at least 4.5:1 for normal text")
    
    if score.text_readability_score < 70:
        recommendations.append("Simplify language and reduce sentence complexity")
        recommendations.append("Break long sentences into shorter, clearer ones")
    
    if score.subtitle_score < 70:
        recommendations.append("Add accurate subtitles or captions to video content")
        recommendations.append("Include descriptions of important sound effects")
    
    if score.overall_score >= 90:
        recommendations.append("Excellent accessibility! Consider sharing your approach with others")
    elif score.overall_score >= 75:
        recommendations.append("Good accessibility foundation - small improvements will make it excellent")
    elif score.overall_score >= 50:
        recommendations.append("Focus on the highest-impact issues first")
    else:
        recommendations.append("Consider using accessibility templates or tools to improve quickly")
    
    return recommendations