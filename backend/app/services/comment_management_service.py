"""
AI-driven comment and inbox management service
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import asyncio
from loguru import logger

from app.models.automation import CommentManagement, CommentAction
from app.models.social_account import SocialAccount
from app.schemas.automation import (
    CommentManagementCreate, CommentManagementUpdate, CommentAnalysisResponse
)


class CommentManagementService:
    """Service for AI-driven comment and inbox management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def process_comment(
        self, 
        comment_data: CommentManagementCreate, 
        user_id: int
    ) -> CommentManagement:
        """Process a new comment with AI analysis"""
        
        # Verify user owns the social account
        social_account_query = select(SocialAccount).where(
            and_(SocialAccount.id == comment_data.social_account_id, SocialAccount.user_id == user_id)
        )
        social_account_result = await self.db.execute(social_account_query)
        social_account = social_account_result.scalar_one_or_none()
        
        if not social_account:
            raise ValueError("Social account not found or not owned by user")
        
        # Create comment management entry
        comment_mgmt = CommentManagement(
            **comment_data.model_dump(),
            user_id=user_id
        )
        
        # Perform AI analysis
        analysis = await self._analyze_comment(comment_data.comment_text)
        
        comment_mgmt.sentiment_score = analysis.sentiment_score
        comment_mgmt.spam_score = analysis.spam_score
        comment_mgmt.toxicity_score = analysis.toxicity_score
        comment_mgmt.ai_summary = analysis.ai_summary
        
        # Determine if it needs attention or is spam
        comment_mgmt.needs_attention = (
            analysis.toxicity_score in ["medium", "high"] or
            analysis.spam_score in ["medium", "high"] or
            analysis.sentiment_score == "negative"
        )
        comment_mgmt.is_spam = analysis.spam_score == "high"
        
        # Take automated action if confidence is high enough
        if analysis.confidence_score >= 0.8:
            comment_mgmt.action_taken = analysis.recommended_action
            
            # Generate auto-response if needed
            if analysis.recommended_action == CommentAction.AUTO_RESPOND:
                comment_mgmt.auto_response = await self._generate_auto_response(
                    comment_data.comment_text, 
                    analysis
                )
            
            comment_mgmt.is_processed = True
            comment_mgmt.processed_at = datetime.utcnow()
        
        # Escalate if needed
        if comment_mgmt.needs_attention and not comment_mgmt.is_processed:
            comment_mgmt.escalated_to_user = True
        
        self.db.add(comment_mgmt)
        await self.db.commit()
        await self.db.refresh(comment_mgmt)
        
        logger.info(f"Processed comment {comment_mgmt.id} for user {user_id}")
        return comment_mgmt
    
    async def get_comment(self, comment_id: int, user_id: int) -> Optional[CommentManagement]:
        """Get a comment management entry by ID"""
        
        query = select(CommentManagement).where(
            and_(CommentManagement.id == comment_id, CommentManagement.user_id == user_id)
        ).options(selectinload(CommentManagement.social_account))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_comments(
        self, 
        user_id: int,
        social_account_id: Optional[int] = None,
        needs_attention: Optional[bool] = None,
        is_spam: Optional[bool] = None,
        is_processed: Optional[bool] = None,
        sentiment: Optional[str] = None,
        page: int = 1, 
        size: int = 20
    ) -> tuple[List[CommentManagement], int]:
        """List comments with filters"""
        
        query = select(CommentManagement).where(CommentManagement.user_id == user_id)
        
        # Apply filters
        if social_account_id:
            query = query.where(CommentManagement.social_account_id == social_account_id)
        
        if needs_attention is not None:
            query = query.where(CommentManagement.needs_attention == needs_attention)
        
        if is_spam is not None:
            query = query.where(CommentManagement.is_spam == is_spam)
        
        if is_processed is not None:
            query = query.where(CommentManagement.is_processed == is_processed)
        
        if sentiment:
            query = query.where(CommentManagement.sentiment_score == sentiment)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(CommentManagement.comment_timestamp)).offset((page - 1) * size).limit(size)
        query = query.options(selectinload(CommentManagement.social_account))
        
        result = await self.db.execute(query)
        comments = list(result.scalars().all())
        
        return comments, total
    
    async def update_comment(
        self, 
        comment_id: int, 
        comment_data: CommentManagementUpdate, 
        user_id: int
    ) -> Optional[CommentManagement]:
        """Update a comment management entry"""
        
        comment = await self.get_comment(comment_id, user_id)
        if not comment:
            return None
        
        update_data = comment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(comment, field, value)
        
        # Mark as processed if action was taken
        if comment_data.action_taken:
            comment.is_processed = True
            comment.processed_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(comment)
        
        logger.info(f"Updated comment {comment_id} for user {user_id}")
        return comment
    
    async def get_comment_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get comment management statistics"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total comments
        total_query = select(func.count()).select_from(CommentManagement).where(
            and_(CommentManagement.user_id == user_id, CommentManagement.created_at >= start_date)
        )
        total_result = await self.db.execute(total_query)
        total_comments = total_result.scalar()
        
        # Comments by sentiment
        sentiment_query = select(
            CommentManagement.sentiment_score, 
            func.count()
        ).where(
            and_(CommentManagement.user_id == user_id, CommentManagement.created_at >= start_date)
        ).group_by(CommentManagement.sentiment_score)
        sentiment_result = await self.db.execute(sentiment_query)
        sentiment_breakdown = {sentiment: count for sentiment, count in sentiment_result.fetchall()}
        
        # Spam detection
        spam_query = select(func.count()).select_from(CommentManagement).where(
            and_(
                CommentManagement.user_id == user_id,
                CommentManagement.created_at >= start_date,
                CommentManagement.is_spam == True
            )
        )
        spam_result = await self.db.execute(spam_query)
        spam_detected = spam_result.scalar()
        
        # Auto-processed vs escalated
        processed_query = select(func.count()).select_from(CommentManagement).where(
            and_(
                CommentManagement.user_id == user_id,
                CommentManagement.created_at >= start_date,
                CommentManagement.is_processed == True,
                CommentManagement.escalated_to_user == False
            )
        )
        processed_result = await self.db.execute(processed_query)
        auto_processed = processed_result.scalar()
        
        escalated_query = select(func.count()).select_from(CommentManagement).where(
            and_(
                CommentManagement.user_id == user_id,
                CommentManagement.created_at >= start_date,
                CommentManagement.escalated_to_user == True
            )
        )
        escalated_result = await self.db.execute(escalated_query)
        escalated = escalated_result.scalar()
        
        # Pending attention
        pending_query = select(func.count()).select_from(CommentManagement).where(
            and_(
                CommentManagement.user_id == user_id,
                CommentManagement.needs_attention == True,
                CommentManagement.is_processed == False
            )
        )
        pending_result = await self.db.execute(pending_query)
        pending_attention = pending_result.scalar()
        
        return {
            "total_comments": total_comments,
            "sentiment_breakdown": sentiment_breakdown,
            "spam_detected": spam_detected,
            "auto_processed": auto_processed,
            "escalated": escalated,
            "pending_attention": pending_attention,
            "automation_rate": round(auto_processed / total_comments * 100, 2) if total_comments > 0 else 0
        }
    
    async def bulk_process_comments(self, user_id: int, social_account_id: int) -> Dict[str, int]:
        """Bulk process pending comments for a social account"""
        
        # Get unprocessed comments
        query = select(CommentManagement).where(
            and_(
                CommentManagement.user_id == user_id,
                CommentManagement.social_account_id == social_account_id,
                CommentManagement.is_processed == False
            )
        )
        
        result = await self.db.execute(query)
        comments = list(result.scalars().all())
        
        processed_count = 0
        escalated_count = 0
        
        for comment in comments:
            try:
                # Re-analyze with updated AI models
                analysis = await self._analyze_comment(comment.comment_text)
                
                comment.sentiment_score = analysis.sentiment_score
                comment.spam_score = analysis.spam_score
                comment.toxicity_score = analysis.toxicity_score
                comment.ai_summary = analysis.ai_summary
                
                # Take action if confidence is high enough
                if analysis.confidence_score >= 0.8:
                    comment.action_taken = analysis.recommended_action
                    comment.is_processed = True
                    comment.processed_at = datetime.utcnow()
                    processed_count += 1
                else:
                    comment.escalated_to_user = True
                    escalated_count += 1
                
            except Exception as e:
                logger.error(f"Error processing comment {comment.id}: {e}")
        
        await self.db.commit()
        
        return {
            "processed": processed_count,
            "escalated": escalated_count,
            "total": len(comments)
        }
    
    async def _analyze_comment(self, comment_text: str) -> CommentAnalysisResponse:
        """Analyze comment using AI (placeholder implementation)"""
        
        # This is a placeholder - in a real implementation, you would:
        # 1. Use OpenAI/GPT API for sentiment analysis
        # 2. Use ML models for spam detection
        # 3. Use toxicity detection models
        # 4. Generate intelligent summaries
        
        # Simple rule-based analysis for demonstration
        text_lower = comment_text.lower()
        
        # Sentiment analysis
        positive_words = ['great', 'awesome', 'love', 'amazing', 'fantastic', 'good', 'excellent']
        negative_words = ['hate', 'terrible', 'awful', 'bad', 'worst', 'stupid', 'sucks']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Spam detection
        spam_indicators = ['buy now', 'click here', 'free money', 'limited offer', 'act now', 'discount']
        spam_count = sum(1 for indicator in spam_indicators if indicator in text_lower)
        
        if spam_count >= 2:
            spam_score = "high"
        elif spam_count == 1:
            spam_score = "medium"
        else:
            spam_score = "low"
        
        # Toxicity detection
        toxic_words = ['idiot', 'stupid', 'hate', 'kill', 'die', 'loser']
        toxic_count = sum(1 for word in toxic_words if word in text_lower)
        
        if toxic_count >= 2:
            toxicity_score = "high"
        elif toxic_count == 1:
            toxicity_score = "medium"
        else:
            toxicity_score = "low"
        
        # Determine recommended action
        if spam_score == "high":
            recommended_action = CommentAction.FILTER_SPAM
        elif toxicity_score == "high":
            recommended_action = CommentAction.DELETE
        elif sentiment == "positive":
            recommended_action = CommentAction.AUTO_RESPOND
        elif sentiment == "negative":
            recommended_action = CommentAction.ESCALATE
        else:
            recommended_action = CommentAction.APPROVE
        
        # Calculate confidence (simple heuristic)
        confidence = 0.7  # Base confidence
        if spam_count > 0 or toxic_count > 0 or positive_count > 0 or negative_count > 0:
            confidence = 0.9
        
        return CommentAnalysisResponse(
            sentiment_score=sentiment,
            spam_score=spam_score,
            toxicity_score=toxicity_score,
            ai_summary=f"Comment with {sentiment} sentiment, {spam_score} spam risk, {toxicity_score} toxicity",
            recommended_action=recommended_action,
            confidence_score=confidence
        )
    
    async def _generate_auto_response(
        self, 
        comment_text: str, 
        analysis: CommentAnalysisResponse
    ) -> str:
        """Generate an appropriate auto-response"""
        
        # This is a placeholder - in a real implementation, you would:
        # 1. Use AI to generate contextual responses
        # 2. Consider brand voice and tone
        # 3. Use templates based on comment type
        
        if analysis.sentiment_score == "positive":
            responses = [
                "Thank you so much! 😊",
                "We really appreciate your kind words!",
                "Thanks for the positive feedback! ❤️",
                "So glad you enjoyed it!"
            ]
        else:
            responses = [
                "Thank you for your comment!",
                "We appreciate you taking the time to share your thoughts.",
                "Thanks for engaging with our content!"
            ]
        
        # Simple random selection - in reality, you'd use AI
        import random
        return random.choice(responses)