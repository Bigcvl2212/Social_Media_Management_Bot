"""
Celery Configuration and Task Definitions
Async task processing for video/image operations, AI generation, and social media posting
"""

import os
from celery import Celery, Task
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta
from typing import Dict, Any

# Initialize Celery
app = Celery(
    'content_manager',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_BACKEND_URL', 'redis://localhost:6379/0')
)

# Configure Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    result_expires=3600,  # Results expire after 1 hour
    task_compression='gzip',
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

logger = get_task_logger(__name__)


# ==================== SCHEDULED TASKS ====================

@app.task(bind=True, max_retries=3)
def process_scheduled_posts(self):
    """
    Check for scheduled posts and publish them
    Runs every 5 minutes
    """
    try:
        from app.models.content import ScheduledPost
        from app.services.platform_integration import PlatformIntegrationService
        
        now = datetime.utcnow()
        integration_service = PlatformIntegrationService()
        
        # Find posts scheduled for now or earlier
        posts_to_publish = ScheduledPost.query.filter(
            ScheduledPost.scheduled_time <= now,
            ScheduledPost.status == 'scheduled'
        ).all()
        
        for post in posts_to_publish:
            try:
                # Post to each platform
                for platform in post.platforms:
                    publish_to_platform.delay(
                        post_id=post.id,
                        platform=platform
                    )
                
                post.status = 'publishing'
                post.save()
                
            except Exception as e:
                logger.error(f"Error publishing post {post.id}: {str(e)}")
                post.status = 'failed'
                post.save()
        
        return {
            'status': 'success',
            'posts_published': len(posts_to_publish)
        }
        
    except Exception as exc:
        logger.error(f"Scheduled posts task failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@app.task(bind=True, max_retries=3)
def collect_analytics(self):
    """
    Collect analytics from all platforms
    Runs every 6 hours
    """
    try:
        from app.models.content import ContentAnalytics, ScheduledPost
        from app.services.platform_integration import PlatformIntegrationService
        
        integration_service = PlatformIntegrationService()
        
        # Get all published posts from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_posts = ScheduledPost.query.filter(
            ScheduledPost.published_at >= thirty_days_ago,
            ScheduledPost.status == 'published'
        ).all()
        
        for post in recent_posts:
            for platform in post.platforms:
                try:
                    analytics = integration_service.get_analytics(
                        platform=platform,
                        post_id=post.platform_post_ids.get(platform)
                    )
                    
                    # Store analytics
                    content_analytics = ContentAnalytics(
                        clip_id=post.clip_id,
                        platform=platform,
                        views=analytics.get('views', 0),
                        likes=analytics.get('likes', 0),
                        comments=analytics.get('comments', 0),
                        shares=analytics.get('shares', 0),
                        saves=analytics.get('saves', 0),
                        engagement_rate=analytics.get('engagement_rate', 0),
                        collected_at=datetime.utcnow()
                    )
                    content_analytics.save()
                    
                except Exception as e:
                    logger.error(f"Error collecting analytics for post {post.id} on {platform}: {str(e)}")
        
        return {
            'status': 'success',
            'posts_analyzed': len(recent_posts)
        }
        
    except Exception as exc:
        logger.error(f"Analytics collection task failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)


# ==================== VIDEO PROCESSING TASKS ====================

@app.task(bind=True, max_retries=5)
def process_video(self, video_path: str, video_id: int):
    """
    Process uploaded video: extract metadata, detect scenes, analyze for clips
    """
    try:
        from app.models.content import ContentJob, GeneratedClip
        from app.services.content_processing import VideoProcessingService
        
        service = VideoProcessingService()
        job = ContentJob.query.get(video_id)
        
        if not job:
            logger.error(f"Video job {video_id} not found")
            return {'status': 'error', 'message': 'Job not found'}
        
        try:
            job.status = 'processing'
            job.save()
            
            logger.info(f"Processing video {video_path}")
            
            # Get video metadata
            metadata = service.get_video_metadata(video_path)
            job.duration_seconds = metadata['duration']
            job.fps = metadata.get('fps', 30)
            job.resolution = metadata.get('resolution', '1920x1080')
            job.save()
            
            # Detect scenes
            scenes = service.detect_scenes(video_path)
            
            # Generate clips from best scenes
            clips = []
            for i, scene in enumerate(scenes[:10]):  # Limit to 10 clips
                clip_data = service.extract_clip(
                    video_path=video_path,
                    start_time=scene['start'],
                    end_time=scene['end']
                )
                
                # Analyze clip for viral potential
                analysis = service.analyze_scene_for_viral_potential(clip_data)
                
                # Create GeneratedClip record
                clip = GeneratedClip(
                    job_id=video_id,
                    clip_filename=f"clip_{i:03d}.mp4",
                    clip_path=clip_data['path'],
                    duration_seconds=clip_data['duration'],
                    aspect_ratio=clip_data.get('aspect_ratio', '16:9'),
                    quality_score=analysis.get('quality_score', 5.0),
                    viral_potential_score=analysis.get('viral_score', 5.0),
                    ai_analysis=analysis,
                    status='pending_review'
                )
                clip.save()
                clips.append(clip)
            
            job.status = 'completed'
            job.clips_generated = len(clips)
            job.completed_at = datetime.utcnow()
            job.save()
            
            logger.info(f"Video processing complete: {len(clips)} clips generated")
            return {
                'status': 'success',
                'clips_generated': len(clips),
                'metadata': metadata
            }
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
            logger.error(f"Video processing error: {str(e)}")
            raise
    
    except Exception as exc:
        logger.error(f"Video processing task failed: {str(exc)}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
        else:
            return {'status': 'failed', 'error': str(exc)}


@app.task(bind=True, max_retries=3)
def extract_audio_transcription(self, video_id: int, video_path: str):
    """
    Extract audio and generate transcription using Groq Whisper
    """
    try:
        from app.models.content import ContentJob
        from app.services.content_processing import VideoProcessingService
        
        service = VideoProcessingService()
        job = ContentJob.query.get(video_id)
        
        logger.info(f"Extracting audio from {video_path}")
        
        # Extract audio
        audio_path = service.extract_audio(video_path)
        
        # Transcribe with Groq
        transcription = service.transcribe_audio(audio_path)
        
        job.transcription = transcription.get('text', '')
        job.save()
        
        return {
            'status': 'success',
            'transcription': transcription
        }
        
    except Exception as exc:
        logger.error(f"Audio transcription task failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


# ==================== IMAGE PROCESSING TASKS ====================

@app.task(bind=True, max_retries=3)
def process_image(self, image_path: str, image_id: int):
    """
    Process uploaded image: apply filters, optimize, analyze
    """
    try:
        from app.models.content import ContentImage
        from app.services.content_processing import ImageProcessingService
        
        service = ImageProcessingService()
        image = ContentImage.query.get(image_id)
        
        if not image:
            logger.error(f"Image {image_id} not found")
            return {'status': 'error'}
        
        try:
            image.status = 'processing'
            image.save()
            
            logger.info(f"Processing image {image_path}")
            
            # Apply trending filters
            filters = ['vintage', 'neon', 'cinematic', 'warm', 'cool']
            processed_images = {}
            
            for filter_name in filters:
                filtered_image = service.apply_filter(
                    image_path=image_path,
                    filter_name=filter_name
                )
                processed_images[filter_name] = filtered_image
            
            # Optimize for different platforms
            optimized_images = {}
            for platform in ['instagram', 'tiktok', 'facebook']:
                optimized = service.optimize_for_platform(
                    image_path=image_path,
                    platform=platform
                )
                optimized_images[platform] = optimized
            
            image.status = 'completed'
            image.processed_images = processed_images
            image.optimized_images = optimized_images
            image.save()
            
            logger.info(f"Image processing complete")
            return {
                'status': 'success',
                'filters_applied': len(filters)
            }
            
        except Exception as e:
            image.status = 'failed'
            image.error_message = str(e)
            image.save()
            raise
    
    except Exception as exc:
        logger.error(f"Image processing task failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


# ==================== AI GENERATION TASKS ====================

@app.task(bind=True, max_retries=3)
def generate_ai_content(self, clip_id: int, content_type: str):
    """
    Generate AI captions, scripts, and enhancement suggestions
    """
    try:
        from app.models.content import GeneratedClip
        from app.services.ai_generation import AIContentGenerationService
        
        service = AIContentGenerationService()
        clip = GeneratedClip.query.get(clip_id)
        
        if not clip:
            logger.error(f"Clip {clip_id} not found")
            return {'status': 'error'}
        
        logger.info(f"Generating AI content for clip {clip_id}")
        
        # Generate captions for different platforms
        captions = {}
        for platform in ['instagram', 'tiktok', 'youtube']:
            caption = service.generate_captions(
                clip_id=clip_id,
                platform=platform,
                ai_analysis=clip.ai_analysis
            )
            captions[platform] = caption
        
        # Generate content ideas
        ideas = service.generate_content_ideas(
            topic=clip.ai_analysis.get('topic', 'General'),
            platform='tiktok',
            count=5
        )
        
        # Store results
        clip.generated_captions = captions
        clip.ai_suggestions = ideas
        clip.status = 'ai_enhanced'
        clip.save()
        
        logger.info(f"AI content generation complete for clip {clip_id}")
        return {
            'status': 'success',
            'captions_generated': len(captions)
        }
        
    except Exception as exc:
        logger.error(f"AI content generation failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=120)


# ==================== SOCIAL MEDIA POSTING TASKS ====================

@app.task(bind=True, max_retries=5)
def publish_to_platform(self, post_id: int, platform: str):
    """
    Publish content to a specific social media platform
    """
    try:
        from app.models.content import ScheduledPost
        from app.services.platform_integration import PlatformIntegrationService
        
        integration_service = PlatformIntegrationService()
        post = ScheduledPost.query.get(post_id)
        
        if not post:
            logger.error(f"Post {post_id} not found")
            return {'status': 'error'}
        
        try:
            logger.info(f"Publishing to {platform}: {post_id}")
            
            post.status = 'publishing'
            post.save()
            
            # Post to platform
            result = integration_service.post_to_platform(
                platform=platform,
                content=post.content,
                caption=post.caption,
                access_token=post.access_tokens.get(platform)
            )
            
            # Store platform-specific post ID
            if not post.platform_post_ids:
                post.platform_post_ids = {}
            post.platform_post_ids[platform] = result.get('post_id')
            
            post.status = 'published'
            post.published_at = datetime.utcnow()
            post.save()
            
            logger.info(f"Successfully published to {platform}")
            return {
                'status': 'success',
                'platform': platform,
                'post_id': result.get('post_id')
            }
            
        except Exception as e:
            post.status = 'failed'
            post.error_message = f"{platform}: {str(e)}"
            post.save()
            logger.error(f"Failed to publish to {platform}: {str(e)}")
            raise
    
    except Exception as exc:
        logger.error(f"Platform publishing task failed: {str(exc)}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
        else:
            return {'status': 'failed', 'error': str(exc)}


# ==================== PERIODIC TASK SCHEDULE ====================

app.conf.beat_schedule = {
    'process-scheduled-posts': {
        'task': 'app.tasks.celery_tasks.process_scheduled_posts',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'collect-analytics': {
        'task': 'app.tasks.celery_tasks.collect_analytics',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
}


if __name__ == '__main__':
    app.start()
