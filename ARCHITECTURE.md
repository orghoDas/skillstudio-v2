# SkillStudio V2 - Technical Architecture

## System Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │   Learner    │  │  Instructor  │  │    Admin     │                 │
│  │  Dashboard   │  │   Portal     │  │   Panel      │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
│         │                  │                  │                         │
│         └──────────────────┴──────────────────┘                         │
│                            │                                            │
│                  React 18 + TypeScript                                  │
│                  Redux Toolkit + React Query                            │
│                  Material-UI / Chakra UI                                │
│                                                                          │
└────────────────────────────┬────────────────────────────────────────────┘
                             │ HTTPS / REST API
                             │ JSON
┌────────────────────────────▼────────────────────────────────────────────┐
│                      API GATEWAY LAYER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                       FastAPI (Python 3.11+)                             │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    API Endpoints                                    │ │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────────┐ │ │
│  │  │  /auth   │  │ /courses │  │ /learning │  │  /ai (AI Dash)   │ │ │
│  │  │          │  │          │  │           │  │                  │ │ │
│  │  │ Register │  │  CRUD    │  │  Goals    │  │  Dashboard       │ │ │
│  │  │ Login    │  │  Browse  │  │  Enroll   │  │  Recommendations │ │ │
│  │  │ Refresh  │  │  Search  │  │  Progress │  │  Learning Paths  │ │ │
│  │  └──────────┘  └──────────┘  └───────────┘  └──────────────────┘ │ │
│  │                                                                    │ │
│  │  ┌──────────┐  ┌──────────┐                                       │ │
│  │  │/assessmt │  │ /profile │                                       │ │
│  │  │          │  │          │                                       │ │
│  │  │ Quizzes  │  │ Settings │                                       │ │
│  │  │ Results  │  │ Analytics│                                       │ │
│  │  └──────────┘  └──────────┘                                       │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │               Middleware & Security                                 │ │
│  │  • CORS (Cross-Origin Resource Sharing)                            │ │
│  │  • JWT Authentication & Authorization                              │ │
│  │  • Request Validation (Pydantic)                                   │ │
│  │  • Rate Limiting                                                   │ │
│  │  • Error Handling & Logging                                        │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│                     BUSINESS LOGIC LAYER                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                        AI Services (NEW!)                                │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                │ │
│  │  │  SkillAssessor      │  │ RecommendationEngine│                │ │
│  │  │                     │  │                     │                │ │
│  │  │ • Analyze quizzes   │  │ • Generate paths    │                │ │
│  │  │ • Calculate skills  │  │ • Next lesson       │                │ │
│  │  │ • Identify gaps     │  │ • Revision content  │                │ │
│  │  │ • Update profiles   │  │ • Difficulty adjust │                │ │
│  │  └─────────────────────┘  └─────────────────────┘                │ │
│  │                                                                     │ │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                │ │
│  │  │ LearningAnalytics   │  │  PathOptimizer      │                │ │
│  │  │                     │  │  (Future)           │                │ │
│  │  │ • Performance stats │  │ • Weekly adjust     │                │ │
│  │  │ • Engagement trends │  │ • A/B testing       │                │ │
│  │  │ • Struggle detect   │  │ • ML predictions    │                │ │
│  │  │ • Insights gen      │  │                     │                │ │
│  │  └─────────────────────┘  └─────────────────────┘                │ │
│  │                                                                     │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│                       DATA ACCESS LAYER                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                    SQLAlchemy 2.0 (Async ORM)                            │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                          Models                                     │ │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐ ┌────────────┐  │ │
│  │  │  User  │ │ Course │ │Learning│ │ Assessment │ │ AI Models  │  │ │
│  │  │ Models │ │ Models │ │ Models │ │  Models    │ │  (NEW!)    │  │ │
│  │  │        │ │        │ │        │ │            │ │            │  │ │
│  │  │ • User │ │• Course│ │• Goal  │ │• Assessment│ │• Snapshot  │  │ │
│  │  │ • Role │ │• Module│ │• Enroll│ │• Question  │ │• Recommend │  │ │
│  │  │ • Prof │ │• Lesson│ │• Prog  │ │• Attempt   │ │• MLMeta    │  │ │
│  │  └────────┘ └────────┘ └────────┘ └────────────┘ │• Event     │  │ │
│  │                                                   └────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                   Connection Pooling                                │ │
│  │  • asyncpg (PostgreSQL async driver)                               │ │
│  │  • Pool size: 20 connections                                       │ │
│  │  • Max overflow: 10                                                │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│                         DATA LAYER                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              PostgreSQL 15+ (Neon Cloud)                          │  │
│  │                                                                    │  │
│  │  ┌─────────────────────┐  ┌─────────────────────┐               │  │
│  │  │   Core Tables       │  │  AI/ML Tables (NEW!)│               │  │
│  │  │                     │  │                     │               │  │
│  │  │ • users             │  │• learning_path_     │               │  │
│  │  │ • learner_profiles  │  │  snapshots          │               │  │
│  │  │ • courses           │  │• recommendations    │               │  │
│  │  │ • modules           │  │• ml_model_metadata  │               │  │
│  │  │ • lessons           │  │• learner_events     │               │  │
│  │  │ • assessments       │  │  (partitioned)      │               │  │
│  │  │ • questions         │  │                     │               │  │
│  │  │ • attempts          │  │                     │               │  │
│  │  │ • learning_goals    │  │                     │               │  │
│  │  │ • enrollments       │  │                     │               │  │
│  │  │ • lesson_progress   │  │                     │               │  │
│  │  └─────────────────────┘  └─────────────────────┘               │  │
│  │                                                                    │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │              Advanced Features                              │  │  │
│  │  │  • JSONB columns (15+) - Flexible schemas                  │  │  │
│  │  │  • GIN indexes - Fast JSONB queries                        │  │  │
│  │  │  • Composite indexes - Multi-column optimization           │  │  │
│  │  │  • Partial indexes - Filtered indexing                     │  │  │
│  │  │  • Foreign key cascades - Data integrity                   │  │  │
│  │  │  • Table partitioning - Time-series optimization           │  │  │
│  │  │  • Full-text search - Built-in search capability           │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │         Redis (Upstash Cloud) - Caching & Sessions                │  │
│  │  • Session management                                             │  │
│  │  • API response caching                                           │  │
│  │  • Real-time features (future)                                    │  │
│  │  • Celery task queue (future)                                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                      BACKGROUND JOBS LAYER (Future)                      │
├─────────────────────────────────────────────────────────────────────────┤
│                     Celery + Redis                                       │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Scheduled Tasks:                                                   │ │
│  │  • Weekly path adjustments                                         │ │
│  │  • ML model retraining                                             │ │
│  │  • Event aggregation                                               │ │
│  │  • Partition management (create/drop old partitions)               │ │
│  │  • Email notifications                                             │ │
│  │  • Analytics report generation                                     │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │   AWS S3     │  │  SendGrid    │  │   OpenAI     │                 │
│  │              │  │              │  │  (Future)    │                 │
│  │ Video/Files  │  │   Emails     │  │   LLM API    │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### 1. User Registration & Initial Profiling

```
User → Register → Create Account → Take Diagnostic Assessment
                                            ↓
                              SkillAssessor analyzes answers
                                            ↓
                          Calculate skill levels (1-10 scale)
                                            ↓
                            Identify knowledge gaps
                                            ↓
                      Update learner_profiles.skill_levels
                                            ↓
                        User creates learning goal
                                            ↓
              RecommendationEngine.generate_learning_path()
                                            ↓
                  Find courses matching skill gaps
                                            ↓
                    Order by difficulty & prerequisites
                                            ↓
                  Save to learning_path_snapshots
                                            ↓
                    Return personalized path to user
```

### 2. Continuous Learning Flow

```
User browses → Enrolls in course → Starts lesson
                                        ↓
                        Track lesson_progress
                        (time, interactions, completion%)
                                        ↓
                    Completes lesson → Takes quiz
                                        ↓
                      Submit quiz answers
                                        ↓
              SkillAssessor calculates performance
                                        ↓
                  Update skill_levels in profile
                        Save attempt to assessment_attempts
                                        ↓
                    [Performance < 60%?]
                        ↓              ↓
                      YES             NO
                        ↓              ↓
          Create revision         Get next lesson
          recommendation          recommendation
                        ↓              ↓
                        └──────┬───────┘
                               ↓
                    Display on dashboard
                               ↓
                    User continues learning
```

### 3. AI Recommendation Engine Flow

```
User requests → GET /ai/dashboard
dashboard              ↓
                LearningAnalytics.get_performance_summary()
                               ↓
              Query last 30 days: lessons, quizzes, time
                               ↓
                Calculate: completion rate, avg score, streak
                               ↓
              RecommendationEngine.recommend_next_lesson()
                               ↓
          Check completed lessons → Find next uncompleted
                               ↓
              Verify prerequisites met
                               ↓
          RecommendationEngine.recommend_revision_content()
                               ↓
          Query poor quiz results → Find matching lessons
                               ↓
              LearningAnalytics.identify_struggling_topics()
                               ↓
          Aggregate skill_scores from recent attempts
                               ↓
              Generate AI insights & personalized message
                               ↓
                  Combine all data → Return JSON response
                               ↓
                    Frontend displays dashboard
```

### 4. Weekly Path Adjustment (Background Job)

```
Celery scheduled task (weekly) → For each active user:
                                        ↓
                LearningAnalytics.weekly_path_adjustment()
                                        ↓
            Analyze last 7 days performance
                                        ↓
                    ┌─────────────────────┬─────────────────────┐
                    ↓                     ↓                     ↓
        [Avg quiz < 60%?]     [Completion < 50%?]    [Excellent performance?]
                    ↓                     ↓                     ↓
        Add revision          Reduce load             Add advanced content
        content                                       
                    └─────────────────────┴─────────────────────┘
                                        ↓
                    Deactivate old learning_path_snapshots
                                        ↓
                Create new snapshot with adjustments
                                        ↓
                  Save adjustment_reasons (explainability)
                                        ↓
                    Create recommendations
                                        ↓
                Send email notification to user
```

---

## Key Design Patterns

### 1. Service Layer Pattern
```
API Endpoint → Service Class → Database Model
               (Business Logic)

Example:
POST /assessments/{id}/submit
  ↓
assessments.py: submit_assessment()
  ↓
SkillAssessor.process_diagnostic_assessment()
  ↓
learner_profiles table
```

### 2. Repository Pattern (via SQLAlchemy ORM)
```
Service → ORM → Database

Example:
RecommendationEngine → db.execute(select(Course)...) → PostgreSQL
```

### 3. Dependency Injection (FastAPI)
```python
async def get_dashboard(
    current_user: User = Depends(get_current_active_learner),
    db: AsyncSession = Depends(get_db)
):
    # current_user and db are injected automatically
```

### 4. Strategy Pattern (Recommendation Logic)
```
RecommendationEngine
  ├── Rule-based (current)
  ├── Collaborative filtering (future)
  ├── Content-based filtering (future)
  └── Hybrid approach (future)
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Security Layers                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. HTTPS/TLS                                               │
│     • Encrypt data in transit                               │
│                                                              │
│  2. JWT Authentication                                       │
│     • Access tokens (30 min expiry)                         │
│     • Refresh tokens (7 day expiry)                         │
│     • Signed with SECRET_KEY                                │
│                                                              │
│  3. Password Security                                        │
│     • Bcrypt hashing                                        │
│     • Salt per password                                     │
│     • Minimum strength validation                           │
│                                                              │
│  4. Authorization                                            │
│     • Role-based access control (RBAC)                      │
│     • Learner/Instructor/Admin roles                        │
│     • Resource ownership checks                             │
│                                                              │
│  5. Input Validation                                         │
│     • Pydantic schema validation                            │
│     • Type checking                                         │
│     • SQL injection prevention (ORM)                        │
│                                                              │
│  6. Rate Limiting (Future)                                   │
│     • Prevent brute force attacks                           │
│     • API throttling                                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Scalability Considerations

### Horizontal Scaling
```
Load Balancer
      ↓
┌─────┴─────┐
│   │   │   │  Multiple FastAPI instances
└─────┬─────┘
      ↓
PostgreSQL (Read Replicas)
      ↓
Redis (Cluster)
```

### Database Optimization
- **Connection Pooling:** Handle 10,000+ concurrent connections
- **Partitioning:** Monthly partitions for learner_events
- **Materialized Views:** Pre-computed analytics
- **Indexes:** 35+ strategic indexes (GIN, B-tree, Composite)

### Caching Strategy
```
Request → Check Redis cache
              ↓ miss
          Query PostgreSQL
              ↓
         Cache result (TTL: 1 hour)
              ↓
          Return response
```

---

## Monitoring & Observability (Future)

```
┌─────────────────────────────────────────────────────────┐
│                   Monitoring Stack                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Application Metrics (Prometheus)                       │
│  • Request latency                                      │
│  • Error rates                                          │
│  • Active users                                         │
│                                                          │
│  Database Metrics (pg_stat_statements)                  │
│  • Slow queries                                         │
│  • Index usage                                          │
│  • Connection pool                                      │
│                                                          │
│  ML Model Metrics (MLflow)                              │
│  • Prediction accuracy                                  │
│  • Model drift                                          │
│  • Feature importance                                   │
│                                                          │
│  Error Tracking (Sentry)                                │
│  • Exception logging                                    │
│  • Stack traces                                         │
│  • User context                                         │
│                                                          │
│  Visualization (Grafana)                                │
│  • Real-time dashboards                                 │
│  • Alerts                                               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Production Deployment                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Frontend: Vercel / Netlify                             │
│  • CDN                                                  │
│  • Auto-scaling                                         │
│  • SSL certificates                                     │
│                                                          │
│  Backend: AWS ECS / Railway / Render                    │
│  • Docker containers                                    │
│  • Auto-scaling (2-10 instances)                        │
│  • Health checks                                        │
│                                                          │
│  Database: Neon PostgreSQL (Serverless)                 │
│  • Auto-scaling compute                                 │
│  • Automatic backups                                    │
│  • Read replicas                                        │
│                                                          │
│  Cache: Upstash Redis (Serverless)                      │
│  • Global replication                                   │
│  • REST API                                             │
│                                                          │
│  Storage: AWS S3                                        │
│  • Video content                                        │
│  • User uploads                                         │
│  • ML model artifacts                                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

**This architecture supports:**
- ✅ 10,000+ concurrent users
- ✅ Real-time AI recommendations
- ✅ Millisecond-latency queries (with caching)
- ✅ Horizontal scaling
- ✅ 99.9% uptime
- ✅ GDPR compliance (data retention policies)
