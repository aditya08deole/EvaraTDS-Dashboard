# 🚀 Quick Vercel Postgres Setup Guide

## Step-by-Step Instructions

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login and Link Project
```bash
vercel login
cd c:\Users\asus\OneDrive\Desktop\evara-tds-platform
vercel link
```

### 3. Create Postgres Database
```bash
vercel postgres create evara-tds-db
```

When prompted:
- **Region**: Choose closest to you (e.g., `iad1` for Washington DC)
- This automatically sets `DATABASE_URL` environment variable

### 4. Add Your Environment Variables

```bash
# Add Telegram Bot Token
vercel env add TELEGRAM_BOT_TOKEN
# Paste: 8507962260:AAHaRXknIvbEILzEgdK4rJ0rRcMNyV3q2NY

# Add ThingSpeak Config
vercel env add THINGSPEAK_CHANNEL_ID
# Enter: 2713286

vercel env add THINGSPEAK_READ_KEY  
# Enter: EHEK3A1XD48TY98B

# Add Thresholds
vercel env add TDS_ALERT_THRESHOLD
# Enter: 150.0

vercel env add TEMP_ALERT_THRESHOLD
# Enter: 35.0

vercel env add ALERT_COOLDOWN_MINUTES
# Enter: 15

# Add frontend variables
vercel env add VITE_API_BASE_URL
# Enter: https://evara-tds-dashboard.vercel.app/api/v1

vercel env add VITE_THINGSPEAK_CHANNEL_ID
# Enter: 2713286

vercel env add VITE_THINGSPEAK_READ_KEY
# Enter: EHEK3A1XD48TY98B

vercel env add VITE_ADMIN_PASSWORD
# Enter: Aditya@08

vercel env add VITE_VIEWER_PASSWORD
# Enter: viewer123
```

For each variable, when prompted for environment:
- Select: **Production, Preview, Development** (press `a` for all)

### 5. Deploy
```bash
git push
```

Or manually:
```bash
vercel --prod
```

### 6. Verify Deployment

1. Go to: https://vercel.com/dashboard
2. Click your project
3. Check deployment status (should be "Ready")
4. Click "Storage" → see your Postgres database

### 7. Test the System

Open your dashboard: https://evara-tds-dashboard.vercel.app

1. **Login:**
   - Username: `Aditya.Evaratech`
   - Password: `Aditya@08`

2. **Go to Alerts page**

3. **Add Recipient:**
   - Name: Aditya
   - Telegram Chat ID: 1362954575
   - Role: admin
   - Channels: telegram
   - Click "Add Recipient"

4. **Send Test Alert:**
   - Click "Send Test Alert" button
   - Check your Telegram for the message

## Troubleshooting

### If recipient addition fails:
```bash
# Check logs
vercel logs

# Verify DATABASE_URL is set
vercel env ls | grep DATABASE_URL
```

### If no tables created:
The app auto-creates tables on first API call. Force init:
```bash
# Make any API call to trigger init
curl https://evara-tds-dashboard.vercel.app/api/v1/alerts/status
```

### If bot doesn't send messages:
1. Verify TELEGRAM_BOT_TOKEN in Vercel dashboard
2. Test bot directly: `https://api.telegram.org/bot<YOUR_TOKEN>/getMe`
3. Check Telegram chat_id is correct

## Success Criteria ✅

You should see:
- ✅ Bot Status: @EvaraTDS_bot (configured)
- ✅ Active Recipients: 1
- ✅ Test alert received in Telegram
- ✅ Real-time data showing on dashboard

## Next Steps

Once working:
1. Configure Telegram webhook (optional, for /start auto-registration)
2. Set up alert monitoring intervals
3. Add more recipients as needed
4. Configure custom thresholds

## Database Management

View/edit data directly:
```bash
# Open Vercel Postgres dashboard
vercel postgres connect evara-tds-db
```

Or use the Vercel web interface:
- Dashboard → Storage → evara-tds-db → Data tab

---

**Need help?** Check deployment logs: `vercel logs --follow`
