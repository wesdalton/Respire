# Supabase Integration Setup Guide

This guide walks you through setting up Supabase authentication and database for the Burnout Predictor application. Supabase provides a cloud-hosted alternative to SQLite, enabling multi-user support, authentication, and scalability.

## Step 1: Create a Supabase Account and Project

1. Go to [Supabase](https://supabase.io/) and sign up for an account
2. Create a new project:
   - Give your project a name (e.g., "burnout-predictor")
   - Choose a strong database password (save this somewhere secure)
   - Select a region closest to your users

## Step 2: Get Your API Keys

1. In your Supabase project dashboard, go to "Settings" > "API"
2. You'll need the following information:
   - **Project URL**: `https://[project-id].supabase.co`
   - **anon/public** key: Used for client-side authentication
   - **service_role** key: Used for server-side operations (keep this secret!)

## Step 3: Set Up Your Environment Variables

Add the following to your `.env` file:

```
# Supabase credentials
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key 
SUPABASE_SERVICE_KEY=your-service-role-key

# Admin user (will be created during initialization)
ADMIN_EMAIL=your-admin-email@example.com
ADMIN_PASSWORD=secure-password-for-admin
```

## Step 4: Initialize Supabase Tables

Run the initialization script to create the necessary tables:

```bash
python init_supabase.py
```

This will:
1. Create the required tables in your Supabase database
2. Create an admin user with the credentials you specified
3. Display the admin user's ID - copy this to your `.env` file:

```
SUPABASE_USER_ID=admin-user-id-from-output
```

## Step 5: Understand the Database Schema

The Supabase implementation uses three main tables:

1. **whoop_tokens**: Stores Whoop API authentication tokens for each user
   - Linked to the `auth.users` table via `user_id`
   - Stores access tokens, refresh tokens, and expiry times

2. **daily_metrics**: Stores the daily health metrics from Whoop and user mood data
   - Linked to the `auth.users` table via `user_id`
   - Each row represents a specific date for a specific user

3. **user_settings**: Stores user-specific settings
   - Linked to the `auth.users` table via `user_id`
   - Stores preferences and integration settings (like calendar integration)

## Step 6: Enable Email Confirmation (Optional)

If you want users to confirm their email addresses:

1. Go to "Authentication" > "Settings"
2. Enable "Email Confirmation" 
3. Customize the confirmation email template if desired

## Step 7: Configure Password Reset (Optional)

To allow users to reset their passwords:

1. Go to "Authentication" > "Settings" > "Auth Providers"
2. Configure "Password Reset" settings
3. Customize the password reset email template

## Step 8: Testing Your Setup

1. Start your Flask application:
   ```bash
   python app.py
   ```

2. Visit the application in your browser and:
   - Create a new account (sign up)
   - Log in with the account
   - Connect your Whoop account
   - Verify data is being stored in Supabase

## Migrating Existing Data

If you have existing data in SQLite that you want to migrate to Supabase:

1. Make sure you've set up the admin user in Supabase
2. Set `SUPABASE_USER_ID` in your `.env` file
3. Run the migration script included in the initialization:
   ```bash
   python init_supabase.py
   ```

This will move your existing Whoop tokens and daily metrics to Supabase under the admin user.

## Troubleshooting

### Authentication Issues

- If users can't sign up or log in, check the Supabase Authentication logs
- Ensure your `SUPABASE_URL` and `SUPABASE_KEY` are correct

### Database Issues

- Check the SQL Editor in Supabase to verify tables were created
- Use the Table Editor to inspect data
- Review the RLS (Row Level Security) policies if you customize them

### API Call Failures

- Check that your service role key has the necessary permissions
- Verify you're using the correct API endpoints

## Next Steps

Once your Supabase integration is working:

1. **Custom Row Level Security**: Set up more advanced RLS policies for multi-user data protection
2. **Real-time Updates**: Use Supabase's real-time capabilities for live dashboard updates
3. **Storage**: Utilize Supabase Storage for file uploads (profile images, etc.)
4. **Edge Functions**: Create serverless functions for advanced processing