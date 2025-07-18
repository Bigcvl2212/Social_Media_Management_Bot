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
- **Docker & Docker Compose** (recommended)
- **Python 3.11+** (for local development)
- **Node.js 18+** (for local development)
- **PostgreSQL** (if not using Docker)
- **Redis** (if not using Docker)

### Option 1: Docker Compose (Recommended)

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
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development

1. **Backend Setup**:
   ```bash
   cd backend
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment
   cp .env.example .env
   # Edit .env with your configuration
   
   # Run the server
   uvicorn main:app --reload
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   
   # Install dependencies
   npm install
   
   # Run the development server
   npm run dev
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/socialmedia_db
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OAuth2 Providers
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret

# AI Services
OPENAI_API_KEY=your-openai-api-key

# Social Media APIs (per-user configuration via UI)
INSTAGRAM_APP_ID=your-instagram-app-id
TWITTER_API_KEY=your-twitter-api-key
# ... etc
```

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
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### End-to-End Tests
```bash
npm run e2e
```

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

## 🚀 Deployment

### Production Deployment

1. **Configure production environment**:
   ```bash
   cp docker/.env.example docker/.env.prod
   # Edit with production values
   ```

2. **Deploy with Docker Compose**:
   ```bash
   docker-compose -f docker/docker-compose.prod.yml up -d
   ```

3. **Set up reverse proxy** (nginx, traefik, etc.)

4. **Configure SSL certificates**

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
