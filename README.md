# Social Media Management Bot 🤖

A next-generation Social Media Management Bot that enables multiple users and teams to manage and grow numerous social media accounts across all major platforms with AI-powered features, comprehensive automation, and a sleek, modern interface.

![Dashboard Preview](https://github.com/user-attachments/assets/7dd6e9fa-6fa8-4497-bd63-abffb2890cca)

## 🚀 Features

### 🎯 Core Capabilities
- **Multi-Account & Multi-User Support**: Collaborative workspace with role-based access control (owner, admin, editor, viewer)
- **Content Ingestion & AI Editing**: Batch upload videos/images with AI-powered video clipping and content generation
- **Viral Content Discovery**: AI-driven trending content recommendations and viral idea generation
- **Scheduling & Automated Posting**: Drag-and-drop content calendar with flexible automation
- **Social Monitoring & Engagement**: Real-time monitoring with AI-powered auto-responses
- **Analytics & Insights**: Unified dashboard with actionable AI-generated suggestions
- **Enterprise Authentication**: Google and Microsoft SSO integration
- **Modern UI/UX**: Responsive React/Next.js interface with dark/light themes

### 🌐 Platform Support
- ✅ Instagram
- ✅ TikTok  
- ✅ YouTube
- ✅ X (Twitter)
- ✅ Facebook
- ✅ LinkedIn
- 🔌 Pluggable architecture for additional platforms

### 🤖 AI-Powered Features
- **Content Generation**: Original images, videos, and text using state-of-the-art models
- **Video Editing**: Automatic clipping of long videos into viral short-form content
- **Caption Generation**: AI-powered post captions and scripts
- **Engagement Optimization**: ML-driven best time recommendations
- **Brand Voice**: Configurable AI responses maintaining consistent brand voice

### 🎭 Multi-Modal AI Features (New!)
- **AI Voiceover & Dubbing**: Multi-language synthesis with voice cloning
- **Image-to-Video Generation**: Transform static images into dynamic videos
- **Enhanced Meme Generator**: Trending, brand-relevant memes with viral analysis
- **Short-Form Video Editor**: AI-powered editing for Reels, TikTok, and Shorts
- **Complete Content Packages**: Multi-platform content creation in one request

## 🏗️ Technical Architecture

### Backend Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Task Queue**: Celery with Redis
- **Authentication**: OAuth2 (Google, Microsoft) + JWT
- **AI Integration**: OpenAI/Gemini, Stable Diffusion, PyTorch
- **File Processing**: FFmpeg, Pillow, OpenCV

### Frontend Stack
- **Framework**: Next.js 15 with TypeScript
- **Styling**: Tailwind CSS with dark/light themes
- **State Management**: TanStack Query (React Query)
- **UI Components**: Headless UI, Heroicons
- **Forms**: React Hook Form with Zod validation
- **Authentication**: NextAuth.js

### DevOps & Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose for local development
- **API Design**: RESTful with automatic OpenAPI documentation
- **Architecture**: Modular, plugin-based design for extensibility

## 📁 Project Structure

```
Social_Media_Management_Bot/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── api/               # API route handlers
│   │   ├── core/              # Core configuration and utilities
│   │   ├── models/            # Database models
│   │   ├── services/          # Business logic services
│   │   ├── plugins/           # Social media platform plugins
│   │   └── utils/             # Utility functions
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend tests
│   └── requirements.txt       # Python dependencies
├── frontend/                  # Next.js frontend application
│   ├── app/                   # Next.js app router
│   ├── components/            # React components
│   │   ├── ui/               # Reusable UI components
│   │   ├── dashboard/        # Dashboard-specific components
│   │   ├── auth/             # Authentication components
│   │   └── content/          # Content management components
│   ├── lib/                   # Utility libraries
│   ├── hooks/                 # Custom React hooks
│   └── types/                 # TypeScript type definitions
├── docker/                    # Docker configuration files
└── docs/                      # Documentation
```

## 🚀 Quick Start

### Prerequisites

Before getting started, ensure you have the following installed:

- **Docker & Docker Compose** (recommended for easy setup)
- **Python 3.11+** (for local development)
- **Node.js 18+** (for frontend development)
- **Git** (for cloning the repository)

**Optional but recommended:**
- **PostgreSQL** (if not using Docker)
- **Redis** (if not using Docker)

### Option 1: Docker Compose (Recommended) 🐳

This is the easiest way to get the entire application running with all dependencies.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Bigcvl2212/Social_Media_Management_Bot.git
   cd Social_Media_Management_Bot
   ```

2. **Start with Docker Compose**:
   ```bash
   # Development environment
   cd docker
   docker-compose up -d
   
   # Production environment
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Access the application**:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

4. **Stop the application**:
   ```bash
   docker-compose down
   ```

### Option 2: Local Development Setup 💻

For development and testing, you can run the backend and frontend separately.

#### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (see Configuration section below)
   ```

5. **Run database migrations** (if using PostgreSQL):
   ```bash
   alembic upgrade head
   ```

6. **Start the backend server**:
   ```bash
   # Development server with auto-reload
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Or simply:
   python main.py
   ```

#### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Start the development server**:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Access the frontend**:
   - Open http://localhost:3000 in your browser

### Option 3: Quick Setup Script 🚀

Use the provided setup script for automated installation:

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup script
./setup.sh

# Follow the interactive prompts
```

The setup script will:
- Check for required dependencies
- Install Python packages
- Set up environment files
- Initialize the database
- Start the development servers

## ⚙️ Configuration

### Environment Variables

The application uses environment variables for configuration. Create `.env` files in the appropriate directories:

#### Backend Configuration (`backend/.env`)

```env
# Development Environment Configuration
DEBUG=true
SECRET_KEY=your-super-secret-key-change-in-production
DATABASE_URL=sqlite+aiosqlite:///./social_media_bot.db
REDIS_URL=redis://localhost:6379/0

# CORS Settings
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# OAuth2 Providers (Get these from respective platforms)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret

# AI Services
OPENAI_API_KEY=your-openai-api-key

# File Upload Settings
MAX_FILE_SIZE=104857600  # 100MB
UPLOAD_DIR=uploads

# Social Media API Keys (Platform-specific)
# Instagram
INSTAGRAM_APP_ID=your-instagram-app-id
INSTAGRAM_APP_SECRET=your-instagram-app-secret

# Twitter/X
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
TWITTER_BEARER_TOKEN=your-twitter-bearer-token

# TikTok
TIKTOK_CLIENT_KEY=your-tiktok-client-key
TIKTOK_CLIENT_SECRET=your-tiktok-client-secret

# Facebook
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret

# LinkedIn
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret

# YouTube
YOUTUBE_API_KEY=your-youtube-api-key
```

#### Frontend Configuration (`frontend/.env.local`)

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1

# Authentication
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret

# OAuth Providers
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
NEXT_PUBLIC_MICROSOFT_CLIENT_ID=your-microsoft-client-id

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_AI_FEATURES=true
NEXT_PUBLIC_ENABLE_VIDEO_PROCESSING=true
```

### Database Configuration

#### SQLite (Development)
```env
DATABASE_URL=sqlite+aiosqlite:///./social_media_bot.db
```

#### PostgreSQL (Production)
```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/social_media_bot
```

#### Database Setup Commands

```bash
# Initialize database
cd backend
alembic upgrade head

# Create new migration (if needed)
alembic revision --autogenerate -m "Description of changes"

# Reset database (development only)
rm social_media_bot.db  # For SQLite
alembic upgrade head
```

### Getting API Keys

To fully utilize the Social Media Management Bot, you'll need API keys from various platforms:

#### Instagram Basic Display API
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app and add Instagram Basic Display product
3. Configure OAuth redirect URIs
4. Copy App ID and App Secret

#### Twitter API v2
1. Apply for access at [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app in your project
3. Generate API Key, API Secret, and Bearer Token
4. Set up OAuth 2.0 with callback URLs

#### TikTok for Developers
1. Register at [TikTok for Developers](https://developers.tiktok.com/)
2. Create a new app
3. Configure Login Kit and Content Posting API
4. Copy Client Key and Client Secret

#### Google APIs (YouTube)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API Key and OAuth 2.0)

#### LinkedIn Developer Platform
1. Create an app at [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Request access to Marketing Developer Platform
3. Configure OAuth 2.0 redirect URLs
4. Copy Client ID and Client Secret

### Security Best Practices

1. **Environment Variables**: Never commit `.env` files to version control
2. **API Keys**: Rotate API keys regularly and use least-privilege access
3. **Database**: Use strong passwords and enable SSL connections
4. **HTTPS**: Always use HTTPS in production
5. **CORS**: Configure ALLOWED_HOSTS properly for your domain
6. **Secrets**: Use a secure secret management system in production

## 📚 API Documentation

The backend automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### Key Endpoints

```
Authentication:
POST /api/v1/auth/register     # User registration
POST /api/v1/auth/login        # User login
GET  /api/v1/auth/me          # Current user info

Content Management:
GET  /api/v1/content          # List content
POST /api/v1/content          # Create content
GET  /api/v1/content/{id}     # Get content details

Social Accounts:
GET  /api/v1/social-accounts  # List connected accounts
POST /api/v1/social-accounts/connect/{platform}  # Connect account

Analytics:
GET  /api/v1/analytics        # Get analytics data
GET  /api/v1/analytics/dashboard  # Dashboard metrics

AI Multi-Modal Features:
POST /api/v1/ai-multimodal/ai-voiceover/generate  # AI voiceover
POST /api/v1/ai-multimodal/image-to-video/create  # Image to video
POST /api/v1/ai-multimodal/enhanced-memes/trending  # Trending memes
POST /api/v1/ai-multimodal/short-form-video/create  # Short-form videos
POST /api/v1/ai-multimodal/multi-modal/complete-package  # Complete package
```

## 🧪 Testing

The Social Media Management Bot includes comprehensive testing to ensure reliability and functionality.

### Test Types

- **Integration Tests**: End-to-end functionality testing
- **Unit Tests**: Individual component testing  
- **API Tests**: REST endpoint validation
- **Authentication Tests**: Security and OAuth flow testing

### Quick Test Execution

```bash
# Run all integration tests
python run_integration_tests.py --verbose --html-report

# Run specific test suite
python run_integration_tests.py --suite authentication

# Run tests for specific platform
python run_integration_tests.py --platform instagram

# Include coverage analysis
python run_integration_tests.py --coverage
```

### Test Suites

#### 1. Authentication Tests
- User registration and login flows
- JWT token management
- Role-based access control
- Team collaboration permissions

#### 2. Social Account Linking Tests  
- OAuth flows for all platforms (Instagram, Twitter, TikTok, etc.)
- Account management and validation
- Token refresh and reauthorization
- Multi-platform account handling

#### 3. Content Posting Tests
- Content creation and publishing
- Multi-platform posting
- Scheduling and automation
- Content management and templates

#### 4. Analytics Tests
- Data retrieval from all platforms
- Cross-platform analytics comparison
- Dashboard generation
- Real-time monitoring and alerts

### Running Tests

```bash
# Backend unit tests
cd backend
pytest tests/ -v

# Frontend tests  
cd frontend
npm test

# Integration tests (from project root)
python run_integration_tests.py
```

### Test Reports

Test execution generates detailed reports:
- **HTML Reports**: Visual test results and coverage
- **Coverage Analysis**: Code coverage metrics
- **Performance Metrics**: Test execution times

For detailed testing documentation, see [TESTING.md](TESTING.md).

## 🔧 Development

### Adding New Social Media Platforms

1. Create a new plugin in `backend/app/plugins/`
2. Implement the platform interface
3. Register the plugin in the platform registry
4. Add frontend integration components

### Adding New AI Features

1. Create service in `backend/app/services/ai/`
2. Implement the AI interface
3. Add API endpoints
4. Create frontend components

## 🚀 Production Deployment

The Social Media Management Bot is now **production-ready** with comprehensive security, monitoring, and operational features.

### ✅ Production Readiness Features

#### Security & Compliance
- **🔐 API Rate Limiting**: Configurable rate limits (1K/10K/50K requests/hour)
- **🛡️ Security Headers**: CSP, HSTS, XSS protection, and more
- **🔒 SSL/HTTPS**: Full SSL termination with modern TLS configuration
- **👥 RBAC**: Role-based access control for teams
- **🔑 OAuth2**: Enterprise authentication (Google, Microsoft)

#### Monitoring & Analytics
- **📊 Error Monitoring**: Sentry integration for real-time error tracking
- **📈 Analytics**: Google Analytics with privacy compliance
- **🔍 Logging**: Comprehensive application and access logging
- **💾 Health Checks**: Automated service health monitoring

#### Database & Backup
- **🗄️ PostgreSQL**: Production-grade database with connection pooling
- **💾 Automated Backups**: Daily backups with configurable retention
- **🔄 Disaster Recovery**: Automated restore procedures
- **📊 Migration Management**: Alembic database migrations

#### Performance & Scalability
- **⚡ Load Balancing**: Nginx reverse proxy with rate limiting
- **🚀 Caching**: Redis caching for improved performance  
- **📦 Container Orchestration**: Docker Compose production setup
- **🌐 CDN Ready**: Optimized for CDN integration

### 🚀 Quick Production Setup

1. **Run Production Readiness Check**:
   ```bash
   ./scripts/production_readiness_check.sh
   ```

2. **Configure Production Environment**:
   ```bash
   cp .env.production .env
   # Edit .env with your production credentials
   ```

3. **Deploy with Docker**:
   ```bash
   cd docker
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Verify Deployment**:
   ```bash
   # Check all services are healthy
   curl https://your-domain.com/health
   curl https://api.your-domain.com/health
   ```

### 🧪 Testing & Validation

#### Load Testing
```bash
# Test with realistic user load
./scripts/load_test.py --users 50 --duration 300
```

#### Security Audit
```bash
# Comprehensive security analysis
./scripts/security_audit.py
```

#### User Acceptance Testing
```bash
# End-to-end functionality testing
./scripts/uat_testing.py --url https://your-domain.com
```

### 📋 Production Checklist

Before going live, ensure you have:

- [ ] **SSL Certificates**: Valid SSL certificates installed
- [ ] **Domain Configuration**: DNS properly configured
- [ ] **Environment Variables**: All production credentials set
- [ ] **Database Setup**: Production database configured and migrated
- [ ] **Monitoring**: Sentry and analytics configured
- [ ] **Backups**: Automated backup procedures tested
- [ ] **Load Testing**: Performance validated under load
- [ ] **Security Audit**: All security checks passed
- [ ] **UAT Testing**: User acceptance tests completed

### 📚 Documentation

- **[Production Deployment Guide](PRODUCTION_DEPLOYMENT.md)**: Complete deployment instructions
- **[Production Ready Improvements](PRODUCTION_READY_IMPROVEMENTS.md)**: Security and feature enhancements
- **[Testing Guide](TESTING.md)**: Comprehensive testing procedures

### 🆘 Production Support

- **Health Monitoring**: `/health` endpoints for service monitoring
- **Error Tracking**: Automatic error reporting via Sentry
- **Log Analysis**: Centralized logging for troubleshooting
- **Backup Procedures**: Automated daily backups with restore capability

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint/Prettier for TypeScript/React code
- Write tests for new features
- Update documentation for API changes
- Use conventional commits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔮 Roadmap

### Phase 1 (Current)
- [x] Core backend architecture
- [x] Modern frontend dashboard
- [x] User authentication
- [x] Basic content management
- [ ] Social media account linking
- [ ] Content scheduling system

### Phase 2 (Next)
- [ ] AI content generation
- [ ] Video processing pipeline
- [ ] Advanced analytics
- [ ] Mobile responsive optimizations
- [ ] Real-time notifications

### Phase 3 (Future)
- [ ] Mobile app (React Native)
- [ ] Advanced workflow automations
- [ ] Custom analytics widgets
- [ ] In-app AI assistant
- [ ] Enterprise features
- [ ] Advanced team collaboration

## 🆘 Support

- 📖 **Documentation**: Check the `/docs` directory
- 🐛 **Bug Reports**: Open an issue on GitHub
- 💡 **Feature Requests**: Open an issue with enhancement label
- 💬 **Discussions**: Use GitHub Discussions
- 📧 **Email**: Contact the maintainers

---

🚀 **Ready to revolutionize your social media management!** This platform provides enterprise-grade social media automation with cutting-edge AI capabilities.
