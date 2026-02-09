# SkillStudio v2 🎓

An AI-powered personalized learning platform built with modern technologies, featuring adaptive learning paths, real-time collaboration, gamification, and comprehensive course management.

## 🌟 Features

### Core Learning Features
- **Course Management** - Complete course creation, enrollment, and progress tracking
- **Interactive Assessments** - Quizzes, assignments, and automated grading
- **Video Content** - Video processing, streaming, and player integration
- **Certificates** - Automated certificate generation upon course completion
- **Progress Tracking** - Detailed analytics and learning path visualization

### AI-Powered Features
- **Personalized Learning Paths** - AI-driven content recommendations
- **Intelligent Tutoring** - AI-powered assistance and feedback
- **Content Analysis** - Automated content tagging and categorization

### Social & Collaboration
- **Real-time Chat** - WebSocket-based messaging system
- **Live Class Sessions** - Schedule and manage live classes with external video platform integration (Zoom, Jitsi, Agora)
- **Collaborative Learning** - Group study sessions and peer interaction
- **Discussion Forums** - Course-specific discussions and Q&A
- **Social Features** - User profiles, followers, and activity feeds

### Engagement & Monetization
- **Gamification** - Points, badges, achievements, and leaderboards
- **Monetization** - Course pricing, payments via Stripe integration
- **Notifications** - Real-time push notifications for important events
- **Reviews & Ratings** - Course rating system with detailed feedback

### Administration
- **Admin Dashboard** - Comprehensive analytics and system management
- **Instructor Portal** - Course creation and student management tools
- **Advanced Analytics** - Engagement metrics, revenue tracking, and performance insights

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL (Neon/asyncpg)
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic
- **Cache/Real-time:** Redis (Upstash)
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt
- **WebSockets:** python-socketio, WebSockets
- **File Storage:** AWS S3 (boto3)
- **Email:** SendGrid
- **Payments:** Stripe
- **PDF Generation:** ReportLab
- **ML/AI:** scikit-learn, NumPy, Pandas

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** Custom components with Lucide icons
- **HTTP Client:** Axios
- **Charts:** Recharts
- **Payments:** Stripe React Components
- **Video:** HLS.js support
- **Date Handling:** date-fns

## 📁 Project Structure

```
skillstudio-v2/
├── backend/
│   ├── alembic/                 # Database migrations
│   │   └── versions/            # Migration files
│   ├── app/
│   │   ├── api/                 # API endpoints
│   │   │   ├── admin.py
│   │   │   ├── admin_analytics.py
│   │   │   ├── ai.py
│   │   │   ├── assessments.py
│   │   │   ├── auth.py
│   │   │   ├── certificates.py
│   │   │   ├── chat.py
│   │   │   ├── collaborative.py
│   │   │   ├── courses.py
│   │   │   ├── dashboard.py
│   │   │   ├── gamification.py
│   │   │   ├── live_class.py
│   │   │   └── ...
│   │   ├── core/                # Core configurations
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── templates/           # Email/PDF templates
│   │   ├── utils/               # Utility functions
│   │   └── main.py              # FastAPI application
│   ├── alembic.ini              # Alembic configuration
│   └── requirements.txt         # Python dependencies
│
└── frontend/
    ├── app/                     # Next.js app directory
    │   ├── admin/               # Admin pages
    │   ├── dashboard/           # Student dashboard
    │   ├── instructor/          # Instructor portal
    │   ├── login/               # Authentication pages
    │   ├── register/
    │   ├── search/              # Search functionality
    │   ├── layout.tsx           # Root layout
    │   └── page.tsx             # Home page
    ├── components/              # React components
    │   ├── AchievementsDisplay.tsx
    │   ├── CertificateDisplay.tsx
    │   ├── ChatInterface.tsx
    │   ├── CourseReviews.tsx
    │   ├── Leaderboard.tsx
    │   ├── NotificationDropdown.tsx
    │   ├── VideoPlayer.tsx
    │   └── ...
    ├── lib/                     # Service layer & utilities
    │   ├── api.ts               # API client configuration
    │   ├── auth.ts              # Authentication utilities
    │   ├── *-service.ts         # Feature-specific services
    │   └── ...
    └── package.json             # Node dependencies
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- Node.js 18+ and npm
- PostgreSQL database (or Neon serverless instance)
- Redis instance (or Upstash Redis)
- AWS S3 bucket (for file storage)
- SendGrid account (for emails)
- Stripe account (for payments)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```env
   # Application
   APP_NAME=SkillStudio
   DEBUG=True
   API_V1_PREFIX=/api/v1
   
   # Security
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Database
   DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
   
   # Redis
   REDIS_URL=redis://localhost:6379
   # OR for Upstash
   UPSTASH_REDIS_URL=your-upstash-url
   UPSTASH_REDIS_TOKEN=your-upstash-token
   
   # CORS
   CORS_ORIGINS=http://localhost:3000,http://localhost:3001
   
   # AWS S3
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your-bucket-name
   
   # SendGrid
   SENDGRID_API_KEY=your-sendgrid-key
   FROM_EMAIL=noreply@yourdomain.com
   
   # Stripe
   STRIPE_SECRET_KEY=your-stripe-secret-key
   STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
   STRIPE_WEBHOOK_SECRET=your-webhook-secret
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create `.env.local` file:**
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   NEXT_PUBLIC_WS_URL=ws://localhost:8000
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:3000`

## 🗄️ Database Migrations

### Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback migration:
```bash
alembic downgrade -1
```

### View migration history:
```bash
alembic history
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user

#### Courses
- `GET /api/v1/courses` - List all courses
- `POST /api/v1/courses` - Create course (instructor)
- `GET /api/v1/courses/{id}` - Get course details
- `POST /api/v1/courses/{id}/enroll` - Enroll in course

#### Assessments
- `GET /api/v1/assessments` - List assessments
- `POST /api/v1/assessments` - Create assessment
- `POST /api/v1/assessments/{id}/submit` - Submit answers

#### Gamification
- `GET /api/v1/gamification/leaderboard` - Get leaderboard
- `GET /api/v1/gamification/achievements` - User achievements
- `GET /api/v1/gamification/badges` - Available badges

#### Chat
- `GET /api/v1/chat/rooms` - List chat rooms
- `POST /api/v1/chat/rooms` - Create chat room
- `GET /api/v1/chat/messages/{room_id}` - Get messages

#### Live Classes
- `GET /api/v1/live-classes` - List live class sessions
- `POST /api/v1/live-classes` - Schedule live class (instructor)
- `GET /api/v1/live-classes/{id}` - Get session details
- `POST /api/v1/live-classes/{id}/start` - Start session
- `POST /api/v1/live-classes/{id}/join` - Join live class

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

## 🔐 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control (Student, Instructor, Admin)
- CORS protection
- SQL injection prevention via ORM
- Input validation with Pydantic
- Secure file upload handling

## 🚢 Deployment

### Backend Deployment (Example with Railway/Render)
1. Set environment variables in your hosting platform
2. Configure PostgreSQL database
3. Run migrations: `alembic upgrade head`
4. Start with: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend Deployment (Vercel)
1. Connect your GitHub repository
2. Set environment variables
3. Deploy with automatic builds

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Style
- **Backend:** Follow PEP 8 guidelines
- **Frontend:** Use ESLint and Prettier configurations
- Write meaningful commit messages
- Add comments for complex logic
- Update documentation for new features

## 📝 License

This project is proprietary and confidential.

## 👥 Team

- **Development Team:** SkillStudio Development
- **Version:** 1.0.0
- **Last Updated:** February 2026

## 📞 Support

For support, email support@skillstudio.com or join our Slack channel.

## 🗺️ Roadmap

### ✅ Completed & Production-Ready (85%)
- **Authentication & Authorization** - JWT, refresh tokens, role-based access
- **Course Management** - Full CRUD with modules, lessons, publishing workflow
- **Learning & Progress** - Enrollment, tracking, completion, time analytics
- **Assessment System** - Auto-grading, adaptive assessments, AI feedback
- **AI Features** - Personalized recommendations, learning paths, skill gap analysis
- **Gamification** - XP, levels, achievements, streaks, leaderboards
- **Social Features** - Reviews, discussions, instructor responses, voting
- **Real-time Chat** - WebSocket messaging, rooms, file sharing
- **Live Class Management** - Scheduling, attendance (integrates with Zoom/Jitsi)
- **Video Processing** - AWS MediaConvert, HLS streaming, analytics
- **Monetization** - Stripe payments, subscriptions, course pricing, instructor payouts
- **Certificates** - PDF generation, verification, QR codes
- **Search & Discovery** - Full-text search, filters, suggestions
- **Admin Dashboard** - User management, analytics, payout approval, moderation
- **Instructor Portal** - Course creation, student analytics, earnings
- **Notifications** - In-app, email (SendGrid), preferences
- **File Management** - S3 uploads, videos, images, documents

### ⚠️ Backend Complete, Frontend UI Needed
- **Live Class UI Pages** - Backend API fully ready (404 lines), needs frontend pages
- **Collaborative Editor** - Backend WebSocket ready, needs Monaco/CodeMirror integration

### 🔧 DevOps & Quality (Pre-Launch Tasks)
- Test suite (pytest + Jest)
- Docker & docker-compose setup
- CI/CD pipeline (GitHub Actions)
- .env.example documentation
- Rate limiting implementation

### ❌ Future Enhancements
- Native WebRTC live streaming (currently uses external platforms)
- Peer-to-peer video calls
- Mobile apps (React Native / Flutter)
- Offline mode & PWA features
- Multi-language support (i18n)
- GraphQL API (currently REST only)
- Plugin/Extension system

---

**Built with ❤️ by the SkillStudio Team**
