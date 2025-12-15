# Backend Implementation Guide

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                    # Configuration and environment variables
│   ├── services/
│   │   ├── __init__.py
│   │   ├── content_processing.py        # Video/Image processing service
│   │   ├── ai_generation.py             # AI content generation service
│   │   └── platform_integration.py      # Social media platform APIs
│   ├── routes/
│   │   ├── __init__.py
│   │   └── content.py                   # Content management API endpoints
│   ├── models/
│   │   └── ... (SQLAlchemy models - existing)
│   └── db/
│       └── ... (Database configuration - existing)
├── requirements.txt                     # Python dependencies
├── .env.example                         # Environment variables template
└── main.py                             # Application starter script
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

**Required API Keys:**

- **Groq API** (Free - 14,400 requests/day)
  - Get key: https://console.groq.com/
  - Used for: Video/image analysis, script generation, content ideas
  
- **OpenAI API** (Paid)
  - Get key: https://platform.openai.com/account/api-keys
  - Used for: Image generation (DALL-E 3)

- **Social Platform Credentials** (Optional for testing)
  - Instagram: Business Account ID + Access Token
  - TikTok: Client ID/Secret + Access Token
  - YouTube: API Key or OAuth credentials
  - Facebook: Page ID + Access Token
  - Twitter/X: Bearer Token
  - LinkedIn: Client ID/Secret

### 3. Install System Dependencies

**FFmpeg** (required for video processing):

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

### 4. Run the Application

```bash
# Development mode (with auto-reload)
python backend/main.py

# Or using Uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## Core Services

### 1. Content Processing Service (`content_processing.py`)

Handles video and image processing:

**VideoProcessingService:**
- `process_video()` - Extract scenes, transcribe audio, analyze for viral clips
  - Detects scene changes using OpenCV
  - Extracts and transcribes audio using Groq Whisper
  - Analyzes each scene for viral potential (1-10 score)
  - Returns structured clip data with metadata

- `_extract_audio()` - FFmpeg audio extraction
- `_transcribe_audio()` - Groq Whisper API integration
- `_detect_scenes()` - OpenCV frame-by-frame comparison
- `_analyze_scene()` - Groq AI scene analysis for viral scoring

**ImageProcessingService:**
- `apply_filter()` - 5 trending filters (Vintage, Neon, Cinematic, Warm, Cool)
- `add_text_overlay()` - Text addition with background for readability
- `optimize_for_platform()` - Platform-specific image sizing (Instagram, TikTok, etc.)

### 2. AI Generation Service (`ai_generation.py`)

AI-powered content generation:

**Text Generation:**
- `generate_captions()` - Platform-optimized captions with hashtags
- `generate_script()` - Video scripts from topics/duration
- `generate_content_ideas()` - Viral content ideas for specific topics
- `analyze_trending_topics()` - Current trending content
- `predict_viral_potential()` - Viral score prediction for content

**Video Generation:**
- `generate_video_from_script()` - AI video generation from script
- `generate_video_from_audio()` - Visual generation from audio/podcast

**Image Generation:**
- `generate_image_from_prompt()` - DALL-E 3 image generation

### 3. Platform Integration Service (`platform_integration.py`)

Multi-platform posting and analytics:

**Supported Platforms:**
- Instagram (Photo + Reels)
- TikTok
- YouTube (Shorts + Long-form)
- Facebook
- Twitter/X
- LinkedIn

**Key Methods:**
- `post_to_instagram()` - Post images/reels
- `post_to_tiktok()` - Upload TikTok videos
- `post_to_youtube()` - Upload YouTube videos
- `post_to_twitter()` - Post tweets with media
- `post_to_facebook()` - Post to Facebook pages
- `post_to_multiple_platforms()` - Simultaneous multi-platform posting

**Analytics:**
- Platform-specific analytics retrieval
- Engagement metrics, reach, impressions
- Follower counts

## API Endpoints

### Content Upload & Processing

```
POST /api/v1/content/upload/video
- Upload video file for processing
- Returns: clips array with viral scores

POST /api/v1/content/upload/image
- Upload image file
```

### Video Editing

```
GET /api/v1/video/{video_id}/clips
- Get detected clips from processed video

POST /api/v1/video/clips/{clip_id}/add-branding
- Add watermark to clip

POST /api/v1/video/clips/{clip_id}/add-music
- Add background music to clip
```

### Image Editing

```
POST /api/v1/image/apply-filter
- Apply filter to image

POST /api/v1/image/add-text
- Add text overlay

POST /api/v1/image/optimize-platform
- Optimize for specific platform
```

### AI Generation

```
POST /api/v1/generate/script
- Generate video script

POST /api/v1/generate/video
- Generate video from script

POST /api/v1/generate/image
- Generate image from prompt

POST /api/v1/generate/video-from-audio
- Generate video from audio file

POST /api/v1/generate/captions
- Generate platform-optimized captions

GET /api/v1/generate/ideas
- Get content ideas

POST /api/v1/analyze/viral-potential
- Analyze viral potential

GET /api/v1/analyze/trending
- Get trending topics
```

### Platform Posting

```
POST /api/v1/post/instagram
POST /api/v1/post/instagram-reel
POST /api/v1/post/tiktok
POST /api/v1/post/youtube
POST /api/v1/post/twitter
POST /api/v1/post/facebook
POST /api/v1/post/multi-platform

GET /api/v1/analytics/{platform}
```

## Integration with Frontend

The frontend React app communicates with these endpoints:

1. **Creation Hub** → `/api/v1/content/upload/video` + `/api/v1/content/upload/image`
2. **Video Clipping Editor** → `/api/v1/video/{id}/clips`
3. **Image Editor** → `/api/v1/image/apply-filter`, `/api/v1/image/add-text`, etc.
4. **AI Generation Workflows** → `/api/v1/generate/script`, `/api/v1/generate/image`, etc.
5. **Platform Manager** → `/api/v1/post/multi-platform`
6. **Growth Analytics** → `/api/v1/analytics/{platform}`

## Testing

### Quick API Test

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Generate captions
curl -X POST http://localhost:8000/api/v1/generate/captions \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "content_description=Gym+fitness+workout&platform=instagram&hashtags=true"

# Get content ideas
curl "http://localhost:8000/api/v1/generate/ideas?topic=fitness&platform=tiktok&count=5"
```

### Unit Testing

```bash
pytest backend/tests -v
```

## Performance Optimization

1. **Video Processing**
   - Large videos (>500MB) split into chunks
   - Scene detection threshold: 27.0 (adjustable)
   - Concurrent clip analysis using asyncio

2. **AI Generation**
   - Groq API: 10x faster than GPT-4
   - Free tier: 14,400 requests/day
   - Rate limiting: Implement with Redis

3. **Image Optimization**
   - Cache filtered images
   - Batch platform optimization
   - Use Pillow for efficient resizing

## Security Considerations

1. **API Keys**
   - Store in `.env` (never commit)
   - Use environment variables
   - Rotate regularly

2. **File Uploads**
   - Validate file types (MIME checking)
   - Limit file sizes
   - Scan for malware

3. **Social Media Credentials**
   - Encrypt stored tokens
   - Implement OAuth 2.0 flow
   - Token refresh handling

## Troubleshooting

### FFmpeg Not Found
```bash
# Windows: Add FFmpeg to PATH or specify in .env
FFMPEG_PATH=C:\ffmpeg\bin\ffmpeg.exe

# Or install globally
choco install ffmpeg
```

### Groq API Rate Limit
- Free tier: 14,400 requests/day
- Implement request queuing with Redis
- Consider batch processing

### Video Processing Timeout
- Increase timeout in config
- Process smaller video chunks
- Use background task queue (Celery)

### CORS Issues
- Check `CORS_ORIGINS` in `.env`
- Ensure frontend URL is whitelisted

## Next Steps

1. **Database Integration**
   - Connect services to SQLAlchemy models
   - Persist clip/content metadata

2. **Background Tasks**
   - Setup Celery for async video processing
   - Implement job queue for large uploads

3. **Caching**
   - Redis caching for processed content
   - API response caching

4. **Monitoring**
   - Sentry for error tracking
   - Logging optimization
   - Performance metrics

5. **Deployment**
   - Docker containerization
   - Cloud deployment (AWS/GCP/Azure)
   - CI/CD pipeline setup
