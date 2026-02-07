# 🚀 Quick Deployment Guide - SkillStudio v2

## Prerequisites

- ✅ PostgreSQL database (Neon recommended - already configured)
- ✅ Node.js 18+ installed
- ✅ Python 3.11+ installed
- ✅ Git repository ready

---

## Local Testing (Before Deployment)

### 1. Backend Setup
```bash
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

**Backend should be running at:** `http://localhost:8000`

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies (includes new Stripe packages)
npm install

# Start development server
npm run dev
```

**Frontend should be running at:** `http://localhost:3000`

### 3. Test the Application

#### Test Accounts:
- **Learner:** `sarah.developer@demo.com` / `demo1234`
- **Instructor:** `emily.instructor@demo.com` / `demo1234`
- **Admin:** (Create one via database or use existing admin account)

#### Test Flow:
1. Login with Sarah's account
2. View AI Dashboard
3. Browse recommended courses
4. Try checkout flow (test mode)
5. Check learning path
6. Switch to Emily's instructor account
7. View instructor dashboard

---

## Production Deployment

### Option A: Quick Deploy (Recommended)

#### Backend: Railway.app
```bash
# 1. Create Railway account: https://railway.app
# 2. Install Railway CLI
npm install -g @railway/cli

# 3. Login to Railway
railway login

# 4. Initialize project in backend directory
cd backend
railway init

# 5. Add PostgreSQL database
railway add --database postgresql

# 6. Set environment variables
railway variables set SECRET_KEY="your-super-secret-key-change-in-production"
railway variables set DATABASE_URL="your-railway-postgres-url"
railway variables set ALGORITHM="HS256"
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"

# 7. Deploy
railway up
```

#### Frontend: Vercel
```bash
# 1. Create Vercel account: https://vercel.com
# 2. Install Vercel CLI
npm install -g vercel

# 3. Deploy from frontend directory
cd frontend
vercel

# 4. Set environment variables in Vercel dashboard
# NEXT_PUBLIC_API_URL=https://your-railway-backend.railway.app
```

---

### Option B: Manual Deploy

#### Backend: Render.com
1. **Create Render Account:** https://render.com
2. **New Web Service:**
   - Connect your GitHub repo
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     - `PYTHON_VERSION=3.11.0`
     - `DATABASE_URL=(your Neon PostgreSQL URL)`
     - `SECRET_KEY=(generate a strong secret)`
     - `ALGORITHM=HS256`
3. **Deploy** - Render will auto-deploy

#### Frontend: Netlify
1. **Create Netlify Account:** https://netlify.com
2. **New Site from Git:**
   - Connect your GitHub repo
   - Base Directory: `frontend`
   - Build Command: `npm run build`
   - Publish Directory: `.next`
   - Environment Variables:
     - `NEXT_PUBLIC_API_URL=(your Render backend URL)`
3. **Deploy** - Netlify will auto-deploy

---

## Environment Variables

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional
REDIS_URL=your-upstash-redis-url
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
STRIPE_SECRET_KEY=sk_test_...
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
# Production:
# NEXT_PUBLIC_API_URL=https://your-backend-url.com

# Optional
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

---

## Database Migration (Production)

```bash
# SSH into your backend server or run locally with production DB URL

# Set production database URL
export DATABASE_URL="your-production-db-url"

# Run migrations
alembic upgrade head

# Generate sample data (optional)
python generate_sample_data.py
```

---

## Post-Deployment Checklist

### Backend
- [ ] API is accessible at production URL
- [ ] Database migrations ran successfully
- [ ] Health check endpoint works: `/docs`
- [ ] CORS configured for frontend URL
- [ ] Environment variables set correctly
- [ ] SSL/HTTPS enabled

### Frontend
- [ ] Site loads at production URL
- [ ] API calls work (check Network tab)
- [ ] Environment variables configured
- [ ] Login/register works
- [ ] Dashboard loads properly
- [ ] Mobile responsive on real devices

### Testing
- [ ] Test user registration
- [ ] Test login flow
- [ ] Test AI recommendations load
- [ ] Test payment flow (test mode)
- [ ] Test admin panel (if admin user exists)
- [ ] Test on mobile device
- [ ] Test on different browsers

---

## Monitoring & Maintenance

### Set Up Monitoring:
1. **Backend Health:** Use UptimeRobot (free) to ping `/docs` endpoint
2. **Error Tracking:** Sentry (free tier) for error monitoring
3. **Analytics:** Umami or Plausible (privacy-friendly analytics)

### Regular Maintenance:
- Check server logs weekly
- Monitor database size
- Update dependencies monthly
- Backup database regularly (Neon auto-backups)
- Review security updates

---

## Troubleshooting

### Frontend can't connect to backend:
```bash
# Check NEXT_PUBLIC_API_URL is correct
console.log(process.env.NEXT_PUBLIC_API_URL)

# Check CORS settings in backend
# backend/app/main.py should have your frontend URL
```

### Database connection issues:
```bash
# Test database connection
python check_database.py

# Check DATABASE_URL format
# Should be: postgresql+asyncpg://...
```

### Build failures:
```bash
# Clear cache and rebuild
# Frontend:
rm -rf .next node_modules package-lock.json
npm install
npm run build

# Backend:
rm -rf __pycache__ venv
python -m venv venv
pip install -r requirements.txt
```

---

## Performance Optimization

### Frontend:
```bash
# Enable Next.js image optimization
# Use next/image for all images

# Enable caching
# Add Cache-Control headers in next.config.js
```

### Backend:
```python
# Enable Redis caching (optional)
# Add connection pooling
# Implement rate limiting
# Add database indexes if slow queries
```

---

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong passwords for demo accounts
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly (don't use *)
- [ ] Validate all user inputs
- [ ] Rate limit API endpoints
- [ ] Keep dependencies updated
- [ ] Use environment variables (never commit secrets)
- [ ] Enable database backups
- [ ] Set up error alerts

---

## Cost Estimate (Free Tier)

- **Railway Backend:** Free tier (500 hours/month)
- **Vercel Frontend:** Free tier (unlimited)
- **Neon PostgreSQL:** Free tier (0.5 GB storage)
- **Upstash Redis:** Free tier (10,000 commands/day)
- **Total:** $0/month

**Upgrade if needed:**
- Railway Pro: $5/month
- Vercel Pro: $20/month
- Neon Pro: $19/month

---

## 🎉 You're Live!

Once deployed, share your URLs:
- **Frontend:** https://skillstudio-v2.vercel.app
- **Backend API:** https://skillstudio-backend.railway.app
- **API Docs:** https://skillstudio-backend.railway.app/docs

**Add to your resume/portfolio:**
- GitHub repo link
- Live demo link
- Video demo link
- Technical blog post about building it

---

## Need Help?

- Check deployment logs for errors
- Review backend logs in Railway/Render dashboard
- Use browser DevTools Network tab
- Check database connection in Neon dashboard
- Review Alembic migration logs

**Congratulations on deploying your AI-powered learning platform! 🚀**
