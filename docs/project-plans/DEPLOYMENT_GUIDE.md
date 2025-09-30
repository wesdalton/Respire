# 🚀 Deployment Guide - Respire

Complete guide to deploying Respire to production cloud services.

---

## Prerequisites

Before deploying, ensure you have accounts for:
- ✅ [GitHub](https://github.com) - Code repository
- ✅ [Vercel](https://vercel.com) - Frontend hosting
- ✅ [Railway](https://railway.app) - Backend hosting
- ✅ [Supabase](https://supabase.com) - Database & Auth
- ✅ [WHOOP Developer](https://developer.whoop.com) - API access

---

## Step 1: Set Up Supabase (Database)

### 1.1 Create Project
1. Go to [https://supabase.com](https://supabase.com)
2. Click "New Project"
3. Choose:
   - **Name**: Respire
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to your users
4. Click "Create new project" (takes ~2 minutes)

### 1.2 Get Credentials
Once project is ready:
1. Go to **Settings** → **API**
2. Copy these values (you'll need them):
   - `Project URL` (SUPABASE_URL)
   - `anon public` key (SUPABASE_KEY)
   - `service_role` key (SUPABASE_SERVICE_KEY)

### 1.3 Set Up Authentication
1. Go to **Authentication** → **Providers**
2. Enable **Email** provider
3. (Optional) Enable **Google OAuth** for social login

### 1.4 Create Database Schema
1. Go to **SQL Editor**
2. Paste and run the schema from `packages/database/schema.sql`
3. Verify tables created successfully

---

## Step 2: Register WHOOP API App

### 2.1 Create Developer Account
1. Go to [https://developer.whoop.com](https://developer.whoop.com)
2. Sign in with your WHOOP account
3. Click "Create New App"

### 2.2 Configure App
- **App Name**: Respire
- **Description**: AI-powered burnout prevention platform
- **Redirect URIs**: (Add these after deployment)
  - `http://localhost:8000/auth/whoop/callback` (for testing)
  - `https://your-api.railway.app/auth/whoop/callback` (production)
- **Scopes**: Select all:
  - `read:profile`
  - `read:cycles`
  - `read:recovery`
  - `read:sleep`
  - `read:workout`
  - `read:body_measurement`

### 2.3 Get Credentials
After creating app:
- Copy `Client ID` (WHOOP_CLIENT_ID)
- Copy `Client Secret` (WHOOP_CLIENT_SECRET)

---

## Step 3: Deploy Backend to Railway

### 3.1 Install Railway CLI (Optional)
```bash
npm install -g @railway/cli
railway login
```

### 3.2 Deploy via GitHub (Recommended)
1. Push code to GitHub
2. Go to [https://railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Choose `apps/api` as root directory
6. Railway will auto-detect Python and deploy

### 3.3 Configure Environment Variables
In Railway dashboard, go to **Variables** and add:

```bash
# Database (from Supabase)
DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# WHOOP API
WHOOP_CLIENT_ID=your-client-id
WHOOP_CLIENT_SECRET=your-client-secret
WHOOP_REDIRECT_URI=https://your-api.railway.app/auth/whoop/callback

# JWT (generate a random secret)
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (get from https://platform.openai.com)
OPENAI_API_KEY=sk-your-key

# Environment
ENVIRONMENT=production
```

### 3.4 Get Your API URL
After deployment:
- Copy your Railway URL: `https://your-app.railway.app`
- Test it: `curl https://your-app.railway.app/health`

---

## Step 4: Deploy Frontend to Vercel

### 4.1 Install Vercel CLI (Optional)
```bash
npm install -g vercel
vercel login
```

### 4.2 Deploy via GitHub (Recommended)
1. Go to [https://vercel.com](https://vercel.com)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Root Directory**: `apps/web`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 4.3 Configure Environment Variables
In Vercel dashboard, go to **Settings** → **Environment Variables**:

```bash
VITE_API_URL=https://your-api.railway.app
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_KEY=your-anon-key
```

### 4.4 Deploy
- Click "Deploy"
- Vercel will build and deploy automatically
- Get your URL: `https://your-app.vercel.app`

---

## Step 5: Configure Redis (Upstash)

### 5.1 Create Database
1. Go to [https://upstash.com](https://upstash.com)
2. Create account (free tier available)
3. Click "Create Database"
4. Choose:
   - **Name**: respire-cache
   - **Region**: Same as Railway
   - **Type**: Regional

### 5.2 Get Redis URL
- Copy the `REDIS_URL` connection string
- Add it to Railway environment variables:
```bash
REDIS_URL=redis://default:[password]@[host]:6379
```

---

## Step 6: Update WHOOP Redirect URI

Now that you have your Railway URL:
1. Go back to WHOOP Developer Dashboard
2. Edit your app
3. Update **Redirect URIs**:
   - Add: `https://your-api.railway.app/auth/whoop/callback`
4. Save changes

---

## Step 7: Set Up Monitoring (Optional but Recommended)

### 7.1 Sentry (Error Tracking)
1. Go to [https://sentry.io](https://sentry.io)
2. Create account (free tier: 5k errors/month)
3. Create project for Respire
4. Copy DSN
5. Add to both Railway and Vercel:
```bash
SENTRY_DSN=https://[key]@[org].ingest.sentry.io/[project]
```

### 7.2 Vercel Analytics
- Automatically enabled in Vercel dashboard
- View at **Analytics** tab

---

## Step 8: Test Production Deployment

### 8.1 Test Backend
```bash
# Health check
curl https://your-api.railway.app/health

# API docs
open https://your-api.railway.app/docs
```

### 8.2 Test Frontend
1. Open `https://your-app.vercel.app`
2. Verify:
   - Page loads
   - Backend connection status shows "Connected"
   - No console errors

### 8.3 Test WHOOP OAuth Flow
1. Click "Connect WHOOP" (when implemented)
2. Should redirect to WHOOP login
3. After auth, should return to your app
4. Data should sync

---

## Step 9: Custom Domain (Optional)

### 9.1 Buy Domain
- Namecheap, Google Domains, etc.
- Recommended: `your-app.com`

### 9.2 Configure Vercel
1. In Vercel dashboard → **Settings** → **Domains**
2. Add your domain
3. Follow DNS configuration instructions

### 9.3 Configure Railway
1. In Railway dashboard → **Settings** → **Domains**
2. Add subdomain: `api.your-app.com`
3. Update WHOOP redirect URI
4. Update frontend API URL

---

## 🎉 You're Live!

Your app is now deployed and accessible:
- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-api.railway.app
- **API Docs**: https://your-api.railway.app/docs
- **Database**: Supabase Dashboard

---

## 📊 Monitoring & Maintenance

### Daily Checks
- ✅ Check Sentry for errors
- ✅ Monitor Railway logs
- ✅ Check Supabase usage

### Weekly Tasks
- 🔄 Review user feedback
- 🔄 Check API rate limits
- 🔄 Review cost dashboard

### Monthly Tasks
- 💰 Review billing
- 📈 Analyze usage metrics
- 🔧 Plan improvements

---

## 🚨 Troubleshooting

### Backend Not Responding
1. Check Railway logs
2. Verify environment variables
3. Check database connection
4. Restart service in Railway dashboard

### Frontend Can't Connect to Backend
1. Verify `VITE_API_URL` in Vercel
2. Check CORS settings in FastAPI
3. Verify Railway deployment is live

### WHOOP OAuth Failing
1. Verify redirect URI exactly matches
2. Check client ID and secret
3. Ensure scopes are correct
4. Check WHOOP API status

---

## 💰 Cost Estimate

### Free Tier (Start Here)
- **Vercel**: Free (100GB bandwidth)
- **Railway**: $5 credit/month (enough for hobby)
- **Supabase**: Free (500MB DB, 2GB bandwidth)
- **Upstash**: Free (10k requests/day)
- **Sentry**: Free (5k events/month)

**Total**: $0-5/month

### Paid Tier (Scale Up Later)
- **Vercel Pro**: $20/month
- **Railway**: ~$10-20/month (usage-based)
- **Supabase Pro**: $25/month
- **OpenAI**: ~$10-20/month (usage-based)

**Total**: ~$65-85/month

---

## 📚 Next Steps

After deployment:
1. ✅ Test all features thoroughly
2. ✅ Set up monitoring alerts
3. ✅ Share URL with beta testers
4. ✅ Gather feedback
5. ✅ Iterate and improve!

---

## 🤝 Need Help?

- Railway Discord: [https://discord.gg/railway](https://discord.gg/railway)
- Vercel Support: [https://vercel.com/support](https://vercel.com/support)
- Supabase Discord: [https://discord.supabase.com](https://discord.supabase.com)