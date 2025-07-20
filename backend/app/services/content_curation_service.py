"""
Content curation service for managing inspiration boards and trend monitoring
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, or_
from sqlalchemy.orm import selectinload
import httpx
import openai
from urllib.parse import urlparse

from app.core.config import settings
from app.models.curation import (
    CurationCollection, CurationItem, TrendWatch, TrendAlert,
    CurationCollectionType, CurationItemType, CurationItemStatus
)
from app.models.social_account import SocialPlatform as Platform
from app.schemas.curation import (
    CurationCollectionCreate, CurationCollectionUpdate,
    CurationItemCreate, CurationItemUpdate,
    TrendWatchCreate, TrendWatchUpdate,
    InspirationBoardSummary, TrendingContentRequest, TrendingContentResponse,
    QuickSaveRequest, BulkItemOperation
)


class ContentCurationService:
    """Service for content curation and inspiration board management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    # Collection Management
    async def create_collection(self, collection_data: CurationCollectionCreate, user_id: int) -> CurationCollection:
        """Create a new curation collection"""
        collection = CurationCollection(
            **collection_data.model_dump(),
            user_id=user_id
        )
        
        self.db.add(collection)
        await self.db.commit()
        await self.db.refresh(collection)
        return collection
    
    async def list_collections(
        self, 
        user_id: int, 
        collection_type: Optional[CurationCollectionType] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[CurationCollection], int]:
        """List user's curation collections with pagination"""
        
        query = select(CurationCollection).where(CurationCollection.user_id == user_id)
        
        if collection_type:
            query = query.where(CurationCollection.collection_type == collection_type)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get collections with item counts
        query = query.order_by(desc(CurationCollection.updated_at))
        query = query.offset((page - 1) * size).limit(size)
        query = query.options(selectinload(CurationCollection.items))
        
        result = await self.db.execute(query)
        collections = result.scalars().all()
        
        return list(collections), total
    
    async def get_collection_by_id(self, collection_id: int, user_id: int) -> Optional[CurationCollection]:
        """Get collection by ID (user must own it)"""
        query = select(CurationCollection).where(
            and_(CurationCollection.id == collection_id, CurationCollection.user_id == user_id)
        ).options(selectinload(CurationCollection.items))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_collection(
        self, 
        collection_id: int, 
        collection_data: CurationCollectionUpdate, 
        user_id: int
    ) -> Optional[CurationCollection]:
        """Update collection (user must own it)"""
        collection = await self.get_collection_by_id(collection_id, user_id)
        if not collection:
            return None
        
        update_data = collection_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(collection, field, value)
        
        await self.db.commit()
        await self.db.refresh(collection)
        return collection
    
    async def delete_collection(self, collection_id: int, user_id: int) -> bool:
        """Delete collection and all its items"""
        collection = await self.get_collection_by_id(collection_id, user_id)
        if not collection:
            return False
        
        await self.db.delete(collection)
        await self.db.commit()
        return True
    
    # Item Management
    async def add_item_to_collection(self, item_data: CurationItemCreate, user_id: int) -> Optional[CurationItem]:
        """Add an item to a collection"""
        # Verify user owns the collection
        collection = await self.get_collection_by_id(item_data.collection_id, user_id)
        if not collection:
            return None
        
        # Create the item
        item = CurationItem(**item_data.model_dump())
        
        # Enhance with AI insights if available
        if self.openai_client:
            ai_insights = await self._generate_ai_insights(item)
            item.ai_insights = ai_insights
            item.viral_potential_score = ai_insights.get("viral_potential_score")
        
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item
    
    async def list_collection_items(
        self,
        collection_id: int,
        user_id: int,
        item_type: Optional[CurationItemType] = None,
        status: Optional[CurationItemStatus] = None,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[CurationItem], int]:
        """List items in a collection with filtering"""
        
        # Verify user owns the collection
        collection = await self.get_collection_by_id(collection_id, user_id)
        if not collection:
            return [], 0
        
        query = select(CurationItem).where(CurationItem.collection_id == collection_id)
        
        # Apply filters
        if item_type:
            query = query.where(CurationItem.item_type == item_type)
        
        if status:
            query = query.where(CurationItem.status == status)
        
        if search:
            query = query.where(
                or_(
                    CurationItem.title.ilike(f"%{search}%"),
                    CurationItem.description.ilike(f"%{search}%"),
                    CurationItem.user_notes.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(CurationItem.created_at))
        query = query.offset((page - 1) * size).limit(size)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def update_item(
        self,
        item_id: int,
        item_data: CurationItemUpdate,
        user_id: int
    ) -> Optional[CurationItem]:
        """Update a curation item"""
        # Get item and verify user owns the collection
        query = select(CurationItem).join(CurationCollection).where(
            and_(CurationItem.id == item_id, CurationCollection.user_id == user_id)
        )
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            return None
        
        update_data = item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        await self.db.commit()
        await self.db.refresh(item)
        return item
    
    async def delete_item(self, item_id: int, user_id: int) -> bool:
        """Delete a curation item"""
        query = select(CurationItem).join(CurationCollection).where(
            and_(CurationItem.id == item_id, CurationCollection.user_id == user_id)
        )
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            return False
        
        await self.db.delete(item)
        await self.db.commit()
        return True
    
    async def mark_item_as_used(self, item_id: int, user_id: int) -> Optional[CurationItem]:
        """Mark an item as used and update usage statistics"""
        query = select(CurationItem).join(CurationCollection).where(
            and_(CurationItem.id == item_id, CurationCollection.user_id == user_id)
        )
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            return None
        
        item.status = CurationItemStatus.USED
        item.times_used += 1
        item.last_used_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(item)
        return item
    
    # Trend Monitoring
    async def create_trend_watch(self, watch_data: TrendWatchCreate, user_id: int) -> TrendWatch:
        """Create a new trend watch"""
        # Verify the auto-save collection exists and belongs to user if specified
        if watch_data.auto_save_to_collection_id:
            collection = await self.get_collection_by_id(watch_data.auto_save_to_collection_id, user_id)
            if not collection:
                watch_data.auto_save_to_collection_id = None
        
        trend_watch = TrendWatch(
            **watch_data.model_dump(),
            user_id=user_id
        )
        
        self.db.add(trend_watch)
        await self.db.commit()
        await self.db.refresh(trend_watch)
        return trend_watch
    
    async def list_trend_watches(self, user_id: int, active_only: bool = False) -> List[TrendWatch]:
        """List user's trend watches"""
        query = select(TrendWatch).where(TrendWatch.user_id == user_id)
        
        if active_only:
            query = query.where(TrendWatch.is_active == True)
        
        query = query.order_by(desc(TrendWatch.created_at))
        query = query.options(selectinload(TrendWatch.alerts))
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_trend_alerts(
        self,
        user_id: int,
        unread_only: bool = False,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[TrendAlert], int]:
        """Get trend alerts for user"""
        
        query = select(TrendAlert).join(TrendWatch).where(TrendWatch.user_id == user_id)
        
        if unread_only:
            query = query.where(TrendAlert.is_read == False)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(TrendAlert.created_at))
        query = query.offset((page - 1) * size).limit(size)
        
        result = await self.db.execute(query)
        alerts = result.scalars().all()
        
        return list(alerts), total
    
    async def mark_alert_as_read(self, alert_id: int, user_id: int) -> bool:
        """Mark a trend alert as read"""
        query = select(TrendAlert).join(TrendWatch).where(
            and_(TrendAlert.id == alert_id, TrendWatch.user_id == user_id)
        )
        result = await self.db.execute(query)
        alert = result.scalar_one_or_none()
        
        if not alert:
            return False
        
        alert.is_read = True
        alert.read_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    # Content Discovery
    async def discover_trending_content(self, request: TrendingContentRequest) -> List[TrendingContentResponse]:
        """Discover trending content across platforms"""
        responses = []
        
        for platform_name in request.platforms:
            try:
                platform = Platform(platform_name)
                trends_data = await self._fetch_platform_trends(
                    platform, request.region, request.time_range, request.keywords
                )
                
                response = TrendingContentResponse(
                    platform=platform_name,
                    trends=trends_data.get("trends", []),
                    hashtags=trends_data.get("hashtags", []),
                    audio_tracks=trends_data.get("audio_tracks"),
                    viral_content=trends_data.get("viral_content", []),
                    generated_at=datetime.utcnow()
                )
                responses.append(response)
                
            except Exception as e:
                print(f"Error fetching trends for {platform_name}: {e}")
                continue
        
        return responses
    
    async def quick_save_content(self, request: QuickSaveRequest, user_id: int) -> Dict[str, Any]:
        """Quick save content from URL to collection"""
        
        # Verify user owns the collection
        collection = await self.get_collection_by_id(request.collection_id, user_id)
        if not collection:
            return {"success": False, "message": "Collection not found"}
        
        try:
            # Extract content metadata from URL
            extracted_data = await self._extract_content_metadata(request.url)
            
            # Determine item type based on URL and extracted data
            item_type = self._determine_item_type(request.url, extracted_data)
            
            # Create the item
            item_data = CurationItemCreate(
                collection_id=request.collection_id,
                item_type=item_type,
                title=request.title or extracted_data.get("title", "Saved Content"),
                description=extracted_data.get("description"),
                source_url=request.url,
                source_platform=extracted_data.get("platform"),
                thumbnail_url=extracted_data.get("thumbnail"),
                item_data=extracted_data,
                user_notes=request.notes,
                user_tags=request.tags
            )
            
            item = await self.add_item_to_collection(item_data, user_id)
            
            return {
                "success": True,
                "item_id": item.id,
                "message": "Content saved successfully",
                "auto_extracted_data": extracted_data
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error saving content: {str(e)}"}
    
    async def get_inspiration_board_summary(self, user_id: int) -> InspirationBoardSummary:
        """Get summary of user's inspiration board"""
        
        # Total collections
        collections_query = select(func.count()).select_from(CurationCollection).where(
            CurationCollection.user_id == user_id
        )
        collections_result = await self.db.execute(collections_query)
        total_collections = collections_result.scalar()
        
        # Total items
        items_query = select(func.count()).select_from(CurationItem).join(CurationCollection).where(
            CurationCollection.user_id == user_id
        )
        items_result = await self.db.execute(items_query)
        total_items = items_result.scalar()
        
        # Collections by type
        type_query = select(CurationCollection.collection_type, func.count()).where(
            CurationCollection.user_id == user_id
        ).group_by(CurationCollection.collection_type)
        type_result = await self.db.execute(type_query)
        collections_by_type = {collection_type.value: count for collection_type, count in type_result.fetchall()}
        
        # Trending items (high viral potential score)
        trending_query = select(CurationItem).join(CurationCollection).where(
            and_(
                CurationCollection.user_id == user_id,
                CurationItem.viral_potential_score >= 7
            )
        ).order_by(desc(CurationItem.viral_potential_score)).limit(5)
        trending_result = await self.db.execute(trending_query)
        trending_items = list(trending_result.scalars().all())
        
        # Recent additions (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_query = select(CurationItem).join(CurationCollection).where(
            and_(
                CurationCollection.user_id == user_id,
                CurationItem.created_at >= week_ago
            )
        ).order_by(desc(CurationItem.created_at)).limit(10)
        recent_result = await self.db.execute(recent_query)
        recent_additions = list(recent_result.scalars().all())
        
        # Active trend watches
        active_watches_query = select(func.count()).select_from(TrendWatch).where(
            and_(TrendWatch.user_id == user_id, TrendWatch.is_active == True)
        )
        active_watches_result = await self.db.execute(active_watches_query)
        active_trend_watches = active_watches_result.scalar()
        
        # Unread alerts
        unread_alerts_query = select(func.count()).select_from(TrendAlert).join(TrendWatch).where(
            and_(TrendWatch.user_id == user_id, TrendAlert.is_read == False)
        )
        unread_alerts_result = await self.db.execute(unread_alerts_query)
        unread_alerts = unread_alerts_result.scalar()
        
        return InspirationBoardSummary(
            total_collections=total_collections,
            total_items=total_items,
            trending_items=trending_items,
            recent_additions=recent_additions,
            active_trend_watches=active_trend_watches,
            unread_alerts=unread_alerts,
            collections_by_type=collections_by_type
        )
    
    async def bulk_operation_items(self, operation: BulkItemOperation, user_id: int) -> Dict[str, Any]:
        """Perform bulk operations on curation items"""
        
        # Get items and verify user owns them
        query = select(CurationItem).join(CurationCollection).where(
            and_(
                CurationItem.id.in_(operation.item_ids),
                CurationCollection.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        items = list(result.scalars().all())
        
        if not items:
            return {"success": False, "processed_items": 0, "failed_items": len(operation.item_ids)}
        
        processed = 0
        failed = 0
        errors = []
        
        try:
            for item in items:
                try:
                    if operation.operation == "move" and operation.target_collection_id:
                        # Verify target collection exists and belongs to user
                        target_collection = await self.get_collection_by_id(operation.target_collection_id, user_id)
                        if target_collection:
                            item.collection_id = operation.target_collection_id
                            processed += 1
                        else:
                            failed += 1
                            errors.append(f"Target collection {operation.target_collection_id} not found")
                    
                    elif operation.operation == "delete":
                        await self.db.delete(item)
                        processed += 1
                    
                    elif operation.operation == "update_status" and operation.new_status:
                        item.status = operation.new_status
                        processed += 1
                    
                    elif operation.operation == "tag":
                        current_tags = item.user_tags or []
                        if operation.tags_to_add:
                            current_tags.extend(operation.tags_to_add)
                        if operation.tags_to_remove:
                            current_tags = [tag for tag in current_tags if tag not in operation.tags_to_remove]
                        item.user_tags = list(set(current_tags))  # Remove duplicates
                        processed += 1
                    
                except Exception as e:
                    failed += 1
                    errors.append(f"Error processing item {item.id}: {str(e)}")
            
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            return {"success": False, "processed_items": 0, "failed_items": len(items), "errors": [str(e)]}
        
        return {
            "success": True,
            "processed_items": processed,
            "failed_items": failed,
            "errors": errors if errors else None
        }
    
    # Private helper methods
    async def _generate_ai_insights(self, item: CurationItem) -> Dict[str, Any]:
        """Generate AI insights for a curation item"""
        if not self.openai_client:
            return {"viral_potential_score": 5}
        
        try:
            prompt = f"""
            Analyze this curated content item and provide insights:
            
            Type: {item.item_type.value}
            Title: {item.title}
            Description: {item.description or "No description"}
            Source Platform: {item.source_platform or "Unknown"}
            Data: {json.dumps(item.item_data or {}, indent=2)}
            
            Provide:
            1. Viral potential score (1-10)
            2. Content category analysis
            3. Trend alignment assessment
            4. Recommended usage tips
            5. Best platforms for this content
            
            Format as JSON.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6
            )
            
            insights = json.loads(response.choices[0].message.content)
            return insights
            
        except Exception as e:
            print(f"Error generating AI insights: {e}")
            return {"viral_potential_score": 5}
    
    async def _fetch_platform_trends(
        self,
        platform: Platform,
        region: str,
        time_range: str,
        keywords: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Fetch trending content from platform APIs (placeholder implementation)"""
        
        # In a real implementation, this would call actual platform APIs
        # For now, return mock data based on platform
        
        mock_data = {
            "trends": [
                {"name": f"{platform.value} Trend 1", "volume": 100000, "growth": "+50%"},
                {"name": f"{platform.value} Trend 2", "volume": 80000, "growth": "+30%"},
                {"name": f"{platform.value} Trend 3", "volume": 60000, "growth": "+20%"},
            ],
            "hashtags": [
                {"tag": f"#{platform.value}trending", "posts": 50000, "engagement": 0.08},
                {"tag": f"#{platform.value}viral", "posts": 30000, "engagement": 0.06},
                {"tag": f"#{platform.value}content", "posts": 20000, "engagement": 0.05},
            ],
            "viral_content": [
                {"title": f"Viral {platform.value} Post 1", "engagement": 1000000, "type": "video"},
                {"title": f"Viral {platform.value} Post 2", "engagement": 800000, "type": "image"},
            ]
        }
        
        # Add audio tracks for TikTok and Instagram
        if platform in [Platform.TIKTOK, Platform.INSTAGRAM]:
            mock_data["audio_tracks"] = [
                {"name": "Trending Audio 1", "usage": 500000, "artist": "Popular Artist"},
                {"name": "Trending Audio 2", "usage": 300000, "artist": "Viral Creator"},
            ]
        
        return mock_data
    
    async def _extract_content_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from content URL (placeholder implementation)"""
        
        # Parse URL to determine platform and content type
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Platform detection
        platform = None
        if "tiktok.com" in domain:
            platform = "tiktok"
        elif "instagram.com" in domain:
            platform = "instagram"
        elif "youtube.com" in domain or "youtu.be" in domain:
            platform = "youtube"
        elif "twitter.com" in domain or "x.com" in domain:
            platform = "twitter"
        elif "linkedin.com" in domain:
            platform = "linkedin"
        
        # Mock extracted data (in real implementation, would use web scraping or platform APIs)
        return {
            "title": f"Content from {platform or 'web'}",
            "description": "Auto-extracted content description",
            "platform": platform,
            "thumbnail": None,
            "content_type": "video" if platform in ["tiktok", "youtube"] else "post",
            "author": "Content Creator",
            "extracted_at": datetime.utcnow().isoformat()
        }
    
    def _determine_item_type(self, url: str, extracted_data: Dict[str, Any]) -> CurationItemType:
        """Determine the appropriate item type based on URL and extracted data"""
        
        platform = extracted_data.get("platform", "").lower()
        content_type = extracted_data.get("content_type", "").lower()
        
        # Check for specific content types
        if "hashtag" in url.lower() or "#" in url or "tag/" in url.lower() or content_type == "hashtag":
            return CurationItemType.HASHTAG
        elif "sound" in url.lower() or "audio" in url.lower() or "music" in url.lower() or content_type == "audio":
            return CurationItemType.AUDIO_TRACK
        elif platform == "tiktok" and "video" in content_type:
            return CurationItemType.INSPIRATION_POST
        elif "template" in url.lower() or "design" in content_type or content_type == "template":
            return CurationItemType.TEMPLATE
        else:
            return CurationItemType.CONTENT_IDEA