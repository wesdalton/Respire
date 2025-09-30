# Supabase Setup Guide

Complete guide to set up Supabase for the Respire application.

## Prerequisites
- Supabase account (free tier is sufficient)
- Email for account creation
- Basic understanding of SQL

## Step 1: Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project" or "New Project"
3. Fill in project details:
   - **Name**: respire-prod (or your preferred name)
   - **Database Password**: Generate a strong password (save this!)
   - **Region**: Choose closest to your users (e.g., US West, US East, EU West)
   - **Pricing Plan**: Free tier is perfect for getting started

4. Click "Create new project"
5. Wait 2-3 minutes for project to initialize

## Step 2: Run Database Schema

1. In your Supabase dashboard, click **SQL Editor** in the left sidebar
2. Click **New query**
3. Open the file `/Users/wesdalton/Desktop/Respire/packages/database/schema.sql`
4. Copy the entire contents
5. Paste into the SQL editor
6. Click **Run** or press Cmd/Ctrl + Enter
7. You should see "Success. No rows returned" - this is expected

### Verify Tables Created

1. Click **Table Editor** in the left sidebar
2. You should see these tables:
   - `whoop_connections`
   - `health_metrics`
   - `mood_ratings`
   - `burnout_scores`
   - `ai_insights`
   - `sync_jobs`
   - `user_preferences`

## Step 3: Enable Row Level Security (RLS)

RLS is already configured in the schema, but verify it's working:

1. Click **Authentication** → **Policies**
2. You should see policies for each table like:
   - "Users can view own WHOOP connection"
   - "Users can insert own health metrics"
   - etc.

If policies are missing, they were included in the schema.sql file.

## Step 4: Get API Credentials

### Project URL
1. In dashboard, click **Settings** → **API**
2. Find **Project URL** (e.g., `https://abcdefgh.supabase.co`)
3. Copy this URL

### API Keys
1. Still on Settings → API page
2. Find **Project API keys** section
3. Copy both keys:
   - **anon public** key (safe to use in frontend)
   - **service_role** key (SECRET - never expose publicly)

### JWT Secret
1. On the same Settings → API page
2. Scroll to **JWT Settings**
3. Copy the **JWT Secret**

## Step 5: Configure Environment Variables

1. Open `/Users/wesdalton/Desktop/Respire/apps/api/.env.example`
2. Create a new file `.env` in the same directory
3. Fill in with your Supabase credentials:

```bash
# Database
DATABASE_URL=postgresql://postgres:[YOUR_DB_PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres

# Supabase
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here

# WHOOP API (get from developer.whoop.com)
WHOOP_CLIENT_ID=your-whoop-client-id
WHOOP_CLIENT_SECRET=your-whoop-client-secret

# OpenAI (get from platform.openai.com)
OPENAI_API_KEY=sk-your-openai-key

# Redis (optional for now)
REDIS_URL=redis://localhost:6379/0
```

### Getting Database URL

The format is:
```
postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
```

- **[PASSWORD]**: The database password you created in Step 1
- **[PROJECT_REF]**: Found in Settings → General → Reference ID

Example:
```
postgresql://postgres:MySecurePassword123@db.abcdefghijklmnop.supabase.co:5432/postgres
```

For the Python asyncpg driver, use:
```
postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
```

## Step 6: Enable Email Authentication

1. Go to **Authentication** → **Providers**
2. Find **Email** provider
3. Make sure it's **Enabled**
4. Configure settings:
   - **Enable email confirmations**: ON (recommended for production)
   - **Enable email change confirmations**: ON
   - **Secure email change**: ON

### Email Templates (Optional but Recommended)

1. Go to **Authentication** → **Email Templates**
2. Customize these templates:
   - **Confirm signup**: Welcome email
   - **Invite user**: Team invitations
   - **Magic Link**: Passwordless login
   - **Change Email Address**: Email change confirmation
   - **Reset Password**: Password reset email

## Step 7: Test Database Connection

1. Restart your API server:
```bash
cd /Users/wesdalton/Desktop/Respire/apps/api
python3 main.py
```

2. Check the health endpoint:
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "checks": {
    "api": "ok",
    "database": "ok",
    "redis": "pending"
  }
}
```

If database shows "ok", connection is successful!

## Step 8: Create Test User (Optional)

You can create a test user via API or Supabase dashboard:

### Via API:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Via Supabase Dashboard:
1. Go to **Authentication** → **Users**
2. Click **Add user** → **Create new user**
3. Fill in email and password
4. Click **Create user**

## Common Issues and Solutions

### Issue: "relation does not exist"
**Solution**: Schema wasn't run. Go back to Step 2 and run schema.sql

### Issue: "connection refused"
**Solution**: Check DATABASE_URL format. Make sure you're using the correct password and project ref.

### Issue: "JWT verification failed"
**Solution**: Check that SUPABASE_JWT_SECRET matches exactly what's in Supabase Settings → API

### Issue: "permission denied for table"
**Solution**: RLS policies might not be applied. Re-run the schema.sql file.

### Issue: "Invalid API key"
**Solution**: Make sure you copied the full anon key and service key from Settings → API

## Security Checklist

Before going to production:

- [ ] Changed default database password
- [ ] Enabled RLS on all tables
- [ ] Verified RLS policies work (test with different users)
- [ ] Stored service_role key securely (never commit to Git)
- [ ] Added `.env` to `.gitignore`
- [ ] Enabled email confirmations
- [ ] Set up custom email templates
- [ ] Configured password requirements (Settings → Authentication)
- [ ] Set up database backups (automatic on paid plans)

## Next Steps

After Supabase is configured:

1. **Register for WHOOP API**
   - Go to [developer.whoop.com](https://developer.whoop.com)
   - Create an application
   - Get OAuth credentials
   - Add to `.env`

2. **Get OpenAI API Key**
   - Go to [platform.openai.com](https://platform.openai.com)
   - Create API key
   - Add to `.env`

3. **Test Full Flow**
   - Register user via `/api/auth/signup`
   - Connect WHOOP via `/api/whoop/auth/authorize`
   - Sync data via `/api/whoop/sync/manual`
   - View data in Supabase Table Editor

## Supabase Dashboard Quick Links

- **Table Editor**: View/edit data
- **SQL Editor**: Run queries
- **Authentication**: Manage users
- **Storage**: File uploads (for future features)
- **Edge Functions**: Serverless functions (for webhooks)
- **Logs**: Monitor queries and errors

## Production Deployment

When deploying to production:

1. **Upgrade to Pro Plan** (if needed):
   - More database resources
   - Automatic backups
   - Priority support
   - Custom domain for auth
   - ~$25/month

2. **Set up monitoring**:
   - Enable logging in Settings → Logs
   - Set up email alerts for errors
   - Monitor database size

3. **Database maintenance**:
   - Vacuum regularly (automatic on Supabase)
   - Monitor slow queries
   - Add indexes as needed

## Support

If you encounter issues:
- Supabase Docs: https://supabase.com/docs
- Community: https://github.com/supabase/supabase/discussions
- Status Page: https://status.supabase.com