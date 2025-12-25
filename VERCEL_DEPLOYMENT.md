# Vercel Deployment Guide for Evara TDS Platform

## Step 1: Set Up Vercel Postgres

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Link your project:**
   ```bash
   vercel link
   ```

4. **Create Postgres database:**
   ```bash
   vercel postgres create
   ```
   - Choose a name (e.g., `evara-tds-db`)
   - Select your region
   - This will automatically set `DATABASE_URL` in your Vercel project

## Step 2: Environment Variables Setup

Go to Vercel Dashboard → Project → Settings → Environment Variables

### Add these variables:

**Backend Environment Variables:**
```
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TDS_ALERT_THRESHOLD=150.0
TEMP_ALERT_THRESHOLD=35.0
ALERT_COOLDOWN_MINUTES=15
THINGSPEAK_CHANNEL_ID=your_channel_id
THINGSPEAK_READ_KEY=your_read_api_key
```

**Note:** `DATABASE_URL` is automatically set when you create Vercel Postgres - don't add it manually!

**Frontend Environment Variables (for Vite build):**
```
VITE_API_BASE_URL=https://your-project.vercel.app/api/v1
VITE_THINGSPEAK_CHANNEL_ID=your_channel_id
VITE_THINGSPEAK_READ_KEY=your_read_api_key
VITE_ADMIN_PASSWORD=your_secure_admin_password
VITE_VIEWER_PASSWORD=your_secure_viewer_password
```

## Step 3: Deploy

```bash
git add .
git commit -m "Add Postgres support for production deployment"
git push
```

Vercel will auto-deploy. Monitor at: https://vercel.com/dashboard

## Step 4: Initialize Database

After first deployment, the database tables will be created automatically.

To verify:
1. Go to Vercel Dashboard → Storage → Your Postgres DB
2. Click "Data" tab
3. You should see 3 tables: `alert_recipients`, `alert_history`, `alert_config`

## Step 5: Add Your First Recipient

**Option A - Via API:**
```bash
curl -X POST "https://your-project.vercel.app/api/v1/alerts/recipients" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Name",
    "telegram_chat_id": "your_chat_id",
    "role": "admin",
    "is_active": true,
    "channels": ["telegram"]
  }'
```

**Option B - Via Dashboard UI:**
1. Go to https://your-project.vercel.app/alerts
2. Click "Add Recipient"
3. Fill in your details
4. Submit

## Step 6: Test Alerts

1. Click "Send Test Alert" in the dashboard
2. Check your Telegram for the message
3. If received → Success! 🎉

## Troubleshooting

### Database Connection Issues
```bash
# Check DATABASE_URL is set
vercel env ls

# View deployment logs
vercel logs
```

### Tables Not Created
The app auto-creates tables on first run. If issues:
1. Check deployment logs for errors
2. Verify DATABASE_URL format
3. Ensure psycopg2-binary is in requirements.txt

### Bot Not Sending Messages
1. Verify TELEGRAM_BOT_TOKEN is set correctly
2. Check bot is not blocked by user
3. Verify chat_id is correct (numeric)

## Production Benefits

✅ **Persistent Storage** - Data survives deployments
✅ **Connection Pooling** - Optimized for serverless
✅ **Auto-scaling** - Handles traffic spikes
✅ **Backups** - Vercel handles automatic backups
✅ **Fast Queries** - Indexed columns for performance
