# Vercel Deployment Guide for Evara TDS Platform

## Environment Variables Setup

You need to add these environment variables to your Vercel project:

### Go to Vercel Dashboard:
1. Visit https://vercel.com/dashboard
2. Select your project: `evara-tds-dashboard`
3. Go to **Settings** → **Environment Variables**

### Add these variables:

```
TELEGRAM_BOT_TOKEN=8507962260:AAHaRXknIvbEILzEgdK4rJ0rRcMNyV3q2NY
TDS_ALERT_THRESHOLD=150.0
TEMP_ALERT_THRESHOLD=35.0
ALERT_COOLDOWN_MINUTES=15
DATABASE_URL=sqlite:///./alerts.db
THINGSPEAK_CHANNEL_ID=2713286
THINGSPEAK_READ_KEY=EHEK3A1XD48TY98B
```

### Important Notes:
- Make sure to select **Production**, **Preview**, and **Development** for all variables
- After adding variables, redeploy the project

## Quick Deploy Commands

```bash
# Commit changes
git add .
git commit -m "Add serverless backend support and environment variables"
git push

# Vercel will auto-deploy on push
```

## Frontend Environment Variables

The frontend is already configured with `.env.production` file that points to:
```
VITE_API_BASE_URL=https://evara-tds-dashboard.vercel.app/api/v1
```

This means API calls will go to the same domain (serverless functions on Vercel).

## Testing After Deployment

1. Visit your deployed site: https://evara-tds-dashboard.vercel.app
2. Go to the **Alerts** page
3. You should see:
   - Bot Status: ✅ @EvaraTDS_bot
   - Active Recipients: 1 (Aditya)
4. Click "Send Test Alert" to verify

## Database Note

⚠️ **Important**: SQLite doesn't work well with serverless functions because they're stateless. For production, you should migrate to a cloud database:

### Recommended Options:
1. **Vercel Postgres** (easiest)
   - Run: `vercel postgres create`
   - Will automatically set DATABASE_URL
   
2. **Supabase** (free tier available)
   - Create account at supabase.com
   - Create project → get PostgreSQL connection string
   - Update DATABASE_URL in Vercel

3. **PlanetScale** (MySQL, free tier)
   - Similar setup to Supabase

### For Now (Quick Fix):
We can use **Vercel KV** (Redis-based) or **Vercel Postgres** for storing recipients.

Would you like me to help you set up Vercel Postgres?
