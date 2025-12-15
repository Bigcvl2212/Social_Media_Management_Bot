# Complete Setup & Launch Guide

## 🎯 Project Overview

This is a **commercial-grade Social Media Content Manager** with:
- ✅ Modern React UI (Next.js 15 + TypeScript)
- ✅ FastAPI backend with async processing
- ✅ Multi-platform posting (Instagram, TikTok, YouTube, Facebook, Twitter, LinkedIn)
- ✅ AI-powered content generation (Groq + OpenAI)
- ✅ Video/image processing and optimization
- ✅ Advanced analytics and trending analysis

## 📋 Prerequisites

### System Requirements
- Python 3.9+
- Node.js 18+
- FFmpeg (for video processing)
- Git

### Accounts & API Keys (Free/Paid)
- **Groq** (Free): https://console.groq.com/ → Get API key
- **OpenAI** (Paid): https://platform.openai.com/account/api-keys
- Social media business accounts (optional for testing)

## 🚀 Quick Start (5 minutes)

### Step 1: Clone & Navigate
```bash
cd Social_Media_Management_Bot
```

### Step 2: Install System Dependencies

**Windows (PowerShell):**
```powershell
choco install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

### Step 3: Backend Setup

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with API keys
copy .env.example .env
# Edit .env and add:
# - GROQ_API_KEY=your-key-here
# - OPENAI_API_KEY=your-key-here
```

### Step 4: Start Backend

```bash
# From backend directory
python main.py
```

Backend runs at: `http://localhost:8000`
- Swagger API Docs: `http://localhost:8000/api/docs`
- Health Check: `http://localhost:8000/api/v1/health`

### Step 5: Frontend Setup (New Terminal)

```bash
# From project root
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: `http://localhost:3000`

## 🧪 Test the System

### Quick API Test

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Generate captions
curl -X POST http://localhost:8000/api/v1/generate/captions \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "content_description=Gym+workout&platform=instagram&hashtags=true"
```

### Run Integration Tests

```bash
# From project root
pip install httpx
python test_integration.py
```

## 📁 Project Structure

```
Social_Media_Management_Bot/
├── frontend/                          # React + Next.js
│   ├── app/
│   │   ├── content/
│   │   │   ├── enhanced-page.tsx     # Main content hub
│   │   │   └── page.tsx              # Router
│   │   └── layout.tsx
│   ├── components/
│   │   └── content/
│   │       ├── creation-hub.tsx       # Upload interface
│   │       ├── video-clipping-editor.tsx
│   │       ├── image-editor.tsx
│   │       ├── content-library.tsx
│   │       ├── content-scheduler.tsx
│   │       ├── growth-analytics.tsx
│   │       ├── platform-manager.tsx
│   │       └── ...more components
│   ├── package.json
│   └── tailwind.config.ts
│
├── backend/                           # FastAPI + Python
│   ├── app/
│   │   ├── main.py                   # FastAPI app
│   │   ├── core/
│   │   │   └── config.py             # Configuration
│   │   ├── services/
│   │   │   ├── content_processing.py # Video/Image
│   │   │   ├── ai_generation.py      # AI Generation
│   │   │   └── platform_integration.py # Social APIs
│   │   ├── routes/
│   │   │   └── content.py            # API endpoints (40+)
│   │   └── models/
│   │       └── (database models)
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
│
├── ENHANCED_CONTENT_MANAGER_UI.md     # Frontend docs
├── BACKEND_IMPLEMENTATION_GUIDE.md    # Backend docs
├── test_integration.py                # Integration tests
└── README.md
```

## 🔑 Setting Up API Keys

### 1. Groq API (Free - Recommended)

```bash
# Visit: https://console.groq.com/
# Sign up → Create API key
# Add to .env:
GROQ_API_KEY=gsk_your-key-here
```

Benefits:
- Free tier: 14,400 requests/day
- 10x faster than GPT-4
- Perfect for content analysis & script generation
- No credit card required

### 2. OpenAI API (Paid)

```bash
# Visit: https://platform.openai.com/account/api-keys
# Sign up → Create API key
# Add to .env:
OPENAI_API_KEY=sk-your-key-here
```

Costs:
- DALL-E 3: $0.04-0.20 per image
- Recommended: Start with $5 credit for testing

### 3. Social Media Setup (Optional)

See `BACKEND_IMPLEMENTATION_GUIDE.md` section "Configure Environment Variables" for detailed setup of:
- Instagram Business Account
- TikTok Creator Account
- YouTube Channel
- Facebook Page
- Twitter/X Account
- LinkedIn Profile

## 🎨 Frontend Features

### Content Creation Hub
- Upload videos for clip extraction
- Upload images for editing
- AI-generated content workflows
- File upload with progress tracking

### Video Clipping Editor
- AI-detected viral clips with scores (1-10)
- Scene-by-scene analysis
- Add branding/watermarks
- Add background music
- Batch edit operations

### Image Editor
- 5 trending filters (Vintage, Neon, Cinematic, Warm, Cool)
- Real-time adjustments (brightness, contrast, saturation, blur)
- Text overlay with backgrounds
- Platform-specific optimization (Instagram, TikTok, etc.)
- Meme template system

### Content Library
- Browse all created content
- Advanced filtering (type, status, viral score)
- Grid/list view switching
- Edit/delete operations

### Analytics Dashboard
- Real-time metrics (reach, engagement, viral videos)
- Platform performance breakdown
- AI-generated growth recommendations

### Platform Manager
- Connect social media accounts
- View account status and follower counts
- Schedule posts across platforms

## 🔄 Complete Workflow Example

### 1. Upload Video
```
Frontend: Drag video to "Creation Hub"
↓
Backend: Process with VideoProcessingService
  - Extract frames & audio
  - Transcribe audio (Groq Whisper)
  - Detect scenes (OpenCV)
  - Analyze viral potential (Groq AI)
↓
Response: Array of detected clips with viral scores
```

### 2. Edit Video Clip
```
Frontend: Select clip → Click "Edit"
↓
Backend: Add branding/music with FFmpeg
↓
Response: Processed video path
```

### 3. Generate Caption
```
Frontend: Enter description → Select platform
↓
Backend: Generate with Groq AI
  - Hook (first 3 words)
  - Body (3-5 sentences)
  - Call-to-action
  - Hashtags
↓
Response: Platform-optimized caption
```

### 4. Post to Multiple Platforms
```
Frontend: Select platforms → Click "Post"
↓
Backend: Post simultaneously using APIs
  - Instagram Graph API
  - TikTok API
  - YouTube API
  - Facebook API
  - Twitter API
↓
Response: Success/failure for each platform
```

## 📊 API Endpoints Summary

### AI Generation (9 endpoints)
- Generate scripts, videos, images, captions
- Analyze trending topics and viral potential
- Get content ideas

### Content Management (5 endpoints)
- Upload video/image
- Get processed clips
- Edit clips (branding, music)

### Image Editing (3 endpoints)
- Apply filters
- Add text overlays
- Optimize for platform

### Platform Posting (7 endpoints)
- Post to individual platforms
- Batch multi-platform posting
- Retrieve analytics

### Authentication (1 endpoint)
- OAuth URL generation for all platforms

**Total: 40+ endpoints**

## 🔧 Development

### Make Changes to Frontend
```bash
cd frontend
npm run dev
# Changes auto-reload at http://localhost:3000
```

### Make Changes to Backend
```bash
cd backend
python main.py
# Changes auto-reload on save
```

### Run Tests
```bash
python test_integration.py
```

### Check Code Quality
```bash
cd backend
black app/  # Format code
flake8 app/  # Lint
mypy app/  # Type checking
```

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check FFmpeg
ffmpeg -version

# Check Groq API key
echo $GROQ_API_KEY  # Should show your key
```

### Frontend Won't Start
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+

# Clear Next.js cache
rm -rf .next
npm run dev
```

### API Calls Failing
```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Check CORS origins in .env
CORS_ORIGINS=http://localhost:3000

# Check API key environment variables
echo $GROQ_API_KEY
echo $OPENAI_API_KEY
```

### Video Processing Timeout
- Process smaller files first
- Increase timeout in config.py
- Use background task queue (Celery) for large videos

## 📚 Documentation

- **Frontend Guide**: `ENHANCED_CONTENT_MANAGER_UI.md`
- **Backend Guide**: `BACKEND_IMPLEMENTATION_GUIDE.md`
- **API Swagger Docs**: `http://localhost:8000/api/docs`

## 🚀 Deployment

### Docker Deployment
```bash
# Build containers
docker-compose up --build

# Access at http://localhost
```

### Cloud Deployment
See `BACKEND_IMPLEMENTATION_GUIDE.md` for:
- AWS deployment
- Google Cloud deployment
- Azure deployment
- Heroku deployment

## 📱 Next Steps

1. ✅ **Setup complete** - Follow steps above
2. 🧪 **Test the API** - Run integration tests
3. 🎨 **Explore UI** - Visit frontend at localhost:3000
4. 📝 **Add content** - Upload videos/images
5. 🔗 **Connect platforms** - OAuth setup (optional)
6. 📊 **View analytics** - See growth metrics

## 💡 Tips & Best Practices

### Content Optimization
- Videos: 15-60 seconds (platform-dependent)
- Images: Use trending filters for engagement
- Captions: Use platform-specific optimization
- Hashtags: 5-10 for optimal reach

### API Rate Limits
- Groq: 14,400 requests/day (free)
- OpenAI: Depends on subscription
- Implement caching for repeated requests

### Performance
- Upload videos <500MB for faster processing
- Cache processed images
- Use multi-platform posting for efficiency

## ❓ FAQ

**Q: Is this free?**
A: Frontend/Backend are open source. Groq API is free (with limits). OpenAI charges per API call.

**Q: How do I add more platforms?**
A: Add platform class in `platform_integration.py`, implement OAuth flow, add API endpoint.

**Q: Can I run this locally?**
A: Yes! No cloud required. Everything runs on your machine.

**Q: How do I deploy to production?**
A: See `BACKEND_IMPLEMENTATION_GUIDE.md` deployment section. Recommend: Docker + AWS/GCP/Heroku.

**Q: Is my data secure?**
A: Yes. Store API keys in `.env` (not committed). Use HTTPS in production.

## 🤝 Support

For issues:
1. Check troubleshooting section above
2. Review API docs at `http://localhost:8000/api/docs`
3. Check logs: `backend/logs/` and browser console

## 🎉 Ready to Go!

You now have a complete, enterprise-grade social media content manager. Start creating viral content! 🚀
