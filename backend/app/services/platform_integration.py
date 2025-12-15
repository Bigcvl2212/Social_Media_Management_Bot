"""
Social Media Platform Integration Service
Handles posting, scheduling, analytics, and API interactions for multiple platforms
"""

import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

import aiohttp
import requests
from instagram_business_sdk import InstagramBusinessAccount
import instagrapi

from app.core.config import settings


class PlatformIntegrationService:
    """Manages social platform integrations"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.platform_configs = {
            'instagram': {
                'base_url': 'https://graph.instagram.com/v18.0',
                'scopes': ['instagram_basic', 'instagram_graph_user_content', 'pages_manage_metadata'],
            },
            'tiktok': {
                'base_url': 'https://open-api.tiktok.com/v1',
                'scopes': ['user.info.basic', 'video.upload', 'video.publish'],
            },
            'youtube': {
                'base_url': 'https://www.googleapis.com/youtube/v3',
                'scopes': ['https://www.googleapis.com/auth/youtube.upload'],
            },
            'facebook': {
                'base_url': 'https://graph.facebook.com/v18.0',
                'scopes': ['pages_manage_posts', 'pages_read_engagement'],
            },
            'twitter': {
                'base_url': 'https://api.twitter.com/2',
                'scopes': ['tweet.write', 'tweet.read', 'users.read'],
            },
            'linkedin': {
                'base_url': 'https://api.linkedin.com/v2',
                'scopes': ['w_member_social', 'r_liteprofile', 'r_basicprofile'],
            },
        }
    
    # ==================== INSTAGRAM ====================
    
    async def post_to_instagram(
        self,
        access_token: str,
        page_id: str,
        image_path: str,
        caption: str,
        hashtags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Post image to Instagram using Graph API"""
        
        try:
            url = f"{self.platform_configs['instagram']['base_url']}/{page_id}/media"
            
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                data = {
                    'image_url': image_path,
                    'caption': caption + (f"\n\n{' '.join(hashtags)}" if hashtags else ""),
                    'access_token': access_token,
                }
                
                response = requests.post(url, data=data)
                media_id = response.json().get('id')
            
            # Publish the media
            publish_url = f"{self.platform_configs['instagram']['base_url']}/{page_id}/media_publish"
            publish_data = {
                'creation_id': media_id,
                'access_token': access_token,
            }
            
            publish_response = requests.post(publish_url, data=publish_data)
            
            return {
                'platform': 'instagram',
                'status': 'posted',
                'post_id': publish_response.json().get('id'),
                'url': f"https://instagram.com/p/{publish_response.json().get('id')}",
                'posted_at': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                'platform': 'instagram',
                'status': 'failed',
                'error': str(e),
            }
    
    async def post_reel_to_instagram(
        self,
        access_token: str,
        page_id: str,
        video_path: str,
        caption: str,
        thumbnail_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Post Reel to Instagram (video)"""
        
        try:
            url = f"{self.platform_configs['instagram']['base_url']}/{page_id}/media"
            
            with open(video_path, 'rb') as video_file:
                files = {'file': video_file}
                data = {
                    'media_type': 'VIDEO',
                    'video_url': video_path,
                    'caption': caption,
                    'access_token': access_token,
                }
                
                if thumbnail_path:
                    with open(thumbnail_path, 'rb') as thumb:
                        data['thumbnail_url'] = thumbnail_path
                
                response = requests.post(url, data=data, files=files)
                media_id = response.json().get('id')
            
            # Publish
            publish_url = f"{self.platform_configs['instagram']['base_url']}/{page_id}/media_publish"
            publish_data = {
                'creation_id': media_id,
                'access_token': access_token,
            }
            
            publish_response = requests.post(publish_url, data=publish_data)
            
            return {
                'platform': 'instagram_reel',
                'status': 'posted',
                'post_id': publish_response.json().get('id'),
                'url': f"https://instagram.com/reel/{publish_response.json().get('id')}",
                'posted_at': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                'platform': 'instagram_reel',
                'status': 'failed',
                'error': str(e),
            }
    
    async def get_instagram_analytics(
        self,
        access_token: str,
        page_id: str,
        metric: str = "impressions,reach,profile_views",
    ) -> Dict[str, Any]:
        """Fetch Instagram analytics"""
        
        try:
            url = f"{self.platform_configs['instagram']['base_url']}/{page_id}/insights"
            params = {
                'metric': metric,
                'period': 'day',
                'access_token': access_token,
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            return {
                'platform': 'instagram',
                'status': 'success',
                'data': data.get('data', []),
                'fetched_at': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                'platform': 'instagram',
                'status': 'failed',
                'error': str(e),
            }
    
    # ==================== TIKTOK ====================
    
    async def post_to_tiktok(
        self,
        access_token: str,
        video_path: str,
        description: str,
        hashtags: Optional[List[str]] = None,
        allow_duets: bool = True,
        allow_stitches: bool = True,
    ) -> Dict[str, Any]:
        """Post video to TikTok"""
        
        try:
            url = f"{self.platform_configs['tiktok']['base_url']}/video/upload/"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            
            with open(video_path, 'rb') as video_file:
                files = {'video': video_file}
                data = {
                    'description': description + (f" {' '.join(hashtags)}" if hashtags else ""),
                    'allow_duets': str(allow_duets).lower(),
                    'allow_stitches': str(allow_stitches).lower(),
                }
                
                response = requests.post(url, headers=headers, data=data, files=files)
            
            response_data = response.json()
            
            return {
                'platform': 'tiktok',
                'status': 'posted' if response.status_code == 200 else 'processing',
                'video_id': response_data.get('data', {}).get('video_id'),
                'posted_at': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                'platform': 'tiktok',
                'status': 'failed',
                'error': str(e),
            }
    
    async def get_tiktok_analytics(
        self,
        access_token: str,
    ) -> Dict[str, Any]:
        """Fetch TikTok channel analytics"""
        
        try:
            url = f"{self.platform_configs['tiktok']['base_url']}/user/info/"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            
            response = requests.get(url, headers=headers)
            data = response.json()
            
            return {
                'platform': 'tiktok',
                'status': 'success',
                'followers': data.get('data', {}).get('user', {}).get('follower_count', 0),
                'following': data.get('data', {}).get('user', {}).get('following_count', 0),
                'video_count': data.get('data', {}).get('user', {}).get('video_count', 0),
                'fetched_at': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                'platform': 'tiktok',
                'status': 'failed',
                'error': str(e),
            }
    
    # ==================== YOUTUBE ====================
    
    async def post_to_youtube(
        self,
        access_token: str,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        privacy_status: str = "public",
        thumbnail_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload video to YouTube"""
        
        try:
            from google.auth.oauthlib.flow import Flow
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            
            youtube = build('youtube', 'v3', credentials=access_token)
            
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': '24',  # Entertainment
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'madeForKids': False,
                },
            }
            
            media = MediaFileUpload(video_path, chunksize=256 * 1024, resumable=True)
            
            request = youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = request.execute()
            
            # Upload thumbnail if provided
            if thumbnail_path:
                youtube.thumbnails().set(
                    videoId=response['id'],
                    media_body=MediaFileUpload(thumbnail_path)
                ).execute()
            
            return {
                'platform': 'youtube',
                'status': 'posted',
                'video_id': response['id'],
                'url': f"https://youtube.com/watch?v={response['id']}",
                'posted_at': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                'platform': 'youtube',
                'status': 'failed',
                'error': str(e),
            }
    
    async def get_youtube_analytics(
        self,
        access_token: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Fetch YouTube channel analytics"""
        
        try:
            from googleapiclient.discovery import build
            
            youtube = build('youtubeAnalytics', 'v2', credentials=access_token)
            
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            
            request = youtube.reports().query(
                ids='channel==MINE',
                startDate=start_date.isoformat(),
                endDate=end_date.isoformat(),
                metrics='views,likes,comments,shares',
                dimensions='day'
            )
            
            response = request.execute()
            
            return {
                'platform': 'youtube',
                'status': 'success',
                'data': response.get('rows', []),
                'column_headers': response.get('columnHeaders', []),
                'fetched_at': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                'platform': 'youtube',
                'status': 'failed',
                'error': str(e),
            }
    
    # ==================== TWITTER/X ====================
    
    async def post_to_twitter(
        self,
        access_token: str,
        text: str,
        media_paths: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Post to Twitter/X API v2"""
        
        try:
            url = f"{self.platform_configs['twitter']['base_url']}/tweets"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'text': text,
            }
            
            # Upload media if provided
            if media_paths:
                media_ids = []
                for media_path in media_paths[:4]:  # Twitter allows max 4 media per tweet
                    media_upload_url = f"{self.platform_configs['twitter']['base_url']}/tweets/search/recent"
                    # Simplified; actual implementation requires separate media upload endpoint
                    media_ids.append(media_path)
                
                payload['media'] = {
                    'media_ids': media_ids
                }
            
            response = requests.post(url, json=payload, headers=headers)
            response_data = response.json()
            
            return {
                'platform': 'twitter',
                'status': 'posted' if response.status_code == 201 else 'pending',
                'tweet_id': response_data.get('data', {}).get('id'),
                'url': f"https://x.com/user/status/{response_data.get('data', {}).get('id')}",
                'posted_at': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                'platform': 'twitter',
                'status': 'failed',
                'error': str(e),
            }
    
    async def get_twitter_analytics(
        self,
        access_token: str,
    ) -> Dict[str, Any]:
        """Fetch Twitter user analytics"""
        
        try:
            url = f"{self.platform_configs['twitter']['base_url']}/users/me"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            
            params = {
                'user.fields': 'public_metrics,created_at,description'
            }
            
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            user_data = data.get('data', {})
            public_metrics = user_data.get('public_metrics', {})
            
            return {
                'platform': 'twitter',
                'status': 'success',
                'followers': public_metrics.get('followers_count', 0),
                'following': public_metrics.get('following_count', 0),
                'tweet_count': public_metrics.get('tweet_count', 0),
                'fetched_at': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                'platform': 'twitter',
                'status': 'failed',
                'error': str(e),
            }
    
    # ==================== FACEBOOK ====================
    
    async def post_to_facebook(
        self,
        access_token: str,
        page_id: str,
        message: str,
        image_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Post to Facebook Page"""
        
        try:
            url = f"{self.platform_configs['facebook']['base_url']}/{page_id}/feed"
            
            data = {
                'message': message,
                'access_token': access_token,
            }
            
            if image_path:
                with open(image_path, 'rb') as image_file:
                    files = {'picture': image_file}
                    response = requests.post(url, data=data, files=files)
            else:
                response = requests.post(url, data=data)
            
            response_data = response.json()
            
            return {
                'platform': 'facebook',
                'status': 'posted',
                'post_id': response_data.get('id'),
                'url': f"https://facebook.com/{response_data.get('id')}",
                'posted_at': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                'platform': 'facebook',
                'status': 'failed',
                'error': str(e),
            }
    
    async def get_facebook_analytics(
        self,
        access_token: str,
        page_id: str,
    ) -> Dict[str, Any]:
        """Fetch Facebook page insights"""
        
        try:
            url = f"{self.platform_configs['facebook']['base_url']}/{page_id}/insights"
            
            params = {
                'metric': 'page_impressions,page_engaged_users,page_post_engagements',
                'period': 'day',
                'access_token': access_token,
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            return {
                'platform': 'facebook',
                'status': 'success',
                'data': data.get('data', []),
                'fetched_at': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                'platform': 'facebook',
                'status': 'failed',
                'error': str(e),
            }
    
    # ==================== MULTI-PLATFORM ====================
    
    async def post_to_multiple_platforms(
        self,
        platforms: List[str],
        content: Dict[str, Any],
        access_tokens: Dict[str, str],
    ) -> Dict[str, Dict[str, Any]]:
        """Post to multiple platforms simultaneously"""
        
        results = {}
        tasks = []
        
        for platform in platforms:
            if platform == 'instagram' and 'image_path' in content:
                task = self.post_to_instagram(
                    access_token=access_tokens.get(platform),
                    page_id=content.get('instagram_page_id'),
                    image_path=content['image_path'],
                    caption=content.get('caption', ''),
                    hashtags=content.get('hashtags'),
                )
            elif platform == 'tiktok' and 'video_path' in content:
                task = self.post_to_tiktok(
                    access_token=access_tokens.get(platform),
                    video_path=content['video_path'],
                    description=content.get('description', ''),
                    hashtags=content.get('hashtags'),
                )
            elif platform == 'youtube' and 'video_path' in content:
                task = self.post_to_youtube(
                    access_token=access_tokens.get(platform),
                    video_path=content['video_path'],
                    title=content.get('title', ''),
                    description=content.get('description', ''),
                    tags=content.get('tags'),
                )
            elif platform == 'twitter':
                task = self.post_to_twitter(
                    access_token=access_tokens.get(platform),
                    text=content.get('caption', '') or content.get('description', ''),
                    media_paths=content.get('media_paths'),
                )
            elif platform == 'facebook':
                task = self.post_to_facebook(
                    access_token=access_tokens.get(platform),
                    page_id=content.get('facebook_page_id'),
                    message=content.get('caption', '') or content.get('description', ''),
                    image_path=content.get('image_path'),
                )
            else:
                results[platform] = {'status': 'skipped', 'reason': 'Unsupported content type'}
                continue
            
            tasks.append((platform, task))
        
        # Execute all tasks concurrently
        for platform, task in tasks:
            try:
                result = await asyncio.create_task(task)
                results[platform] = result
            except Exception as e:
                results[platform] = {
                    'status': 'failed',
                    'error': str(e),
                }
        
        return results
    
    # ==================== OAUTH HELPERS ====================
    
    def get_oauth_url(
        self,
        platform: str,
        client_id: str,
        redirect_uri: str,
        state: str,
    ) -> str:
        """Generate OAuth authorization URL"""
        
        oauth_urls = {
            'instagram': f"https://api.instagram.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=user_profile,user_media&response_type=code&state={state}",
            'tiktok': f"https://www.tiktok.com/v1/oauth/authorize?client_key={client_id}&response_type=code&scope=user.info.basic,video.upload&redirect_uri={redirect_uri}&state={state}",
            'youtube': f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=https://www.googleapis.com/auth/youtube.upload&state={state}",
            'facebook': f"https://www.facebook.com/v18.0/dialog/oauth?client_id={client_id}&redirect_uri={redirect_uri}&scope=pages_manage_posts,pages_read_engagement&state={state}",
            'twitter': f"https://twitter.com/i/oauth2/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=tweet.write%20tweet.read%20users.read&state={state}",
            'linkedin': f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=w_member_social&state={state}",
        }
        
        return oauth_urls.get(platform, "")


# Service instance
platform_integration_service = PlatformIntegrationService()
