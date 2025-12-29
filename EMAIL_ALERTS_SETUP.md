# Email Alert System Setup Guide

## Overview
The EvaraTDS platform now includes an automated email alert system that sends notifications when water quality parameters exceed configured thresholds.

## Features
- ✅ Automated email alerts for TDS and Temperature thresholds
- ✅ Recipient management (add/remove email addresses)
- ✅ Smart throttling (1 email per 15 minutes to prevent spam)
- ✅ Professional HTML email templates
- ✅ Free tier service (300 emails/day with Brevo)
- ✅ Alert history tracking

## Setup Instructions

### 1. Sign Up for Brevo (Recommended Free Service)
1. Go to [Brevo.com](https://www.brevo.com/) (formerly SendinBlue)
2. Click "Sign up free"
3. Create your account (free tier includes 300 emails/day)
4. Verify your email address

### 2. Get Your API Key
1. Log in to your Brevo dashboard
2. Go to **Settings** → **API Keys**
3. Click **Generate a new API key**
4. Give it a name (e.g., "EvaraTDS Alerts")
5. Copy the generated API key (keep it secure!)

### 3. Configure Environment Variables

#### For Local Development:
Create a `.env` file in the `backend` directory:
```bash
BREVO_API_KEY=your_api_key_here
```

#### For Vercel Deployment:
1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add a new variable:
   - **Name**: `BREVO_API_KEY`
   - **Value**: Your Brevo API key
   - **Environment**: Production, Preview, Development
4. Click **Save**
5. Redeploy your project

### 4. Add Recipients
1. Log in to your dashboard
2. Navigate to **Email Alerts** page (📧 icon in sidebar)
3. Add recipients:
   - Enter recipient name
   - Enter valid email address
   - Click "Add Recipient"
4. Recipients will receive alerts when thresholds are exceeded

### 5. Configure Thresholds
1. Go to **Calibration** page (⚙️ icon)
2. Set your desired thresholds:
   - **TDS Threshold** (default: 150 PPM)
   - **Temperature Threshold** (default: 35°C)
3. Changes sync instantly across all devices

## How It Works

### Alert Triggering
The system checks sensor values every 60 seconds:
- If **TDS** exceeds threshold → Email sent to all recipients
- If **Temperature** exceeds threshold → Email sent to all recipients

### Throttling (Anti-Spam)
- Each alert type is throttled independently
- Maximum 1 email per 15 minutes per alert type
- Prevents inbox flooding during sustained high readings

### Email Content
Professional HTML emails include:
- **Current reading** (highlighted in large text)
- **Configured threshold**
- **Timestamp** (UTC)
- **Action required** message
- EvaraTech & IIITH branding

## Alert Email Examples

### TDS Alert Email
```
Subject: 🚨 CRITICAL: High TDS Detected - 409.0 PPM

The Total Dissolved Solids (TDS) level has exceeded the configured threshold.

Current TDS: 409.0 PPM
Threshold: 150.0 PPM
Time: 2025-12-29 10:45:30 UTC

⚠️ Action Required: Please check the water quality monitoring system
```

### Temperature Alert Email
```
Subject: 🌡️ WARNING: High Temperature Detected - 38.5°C

The water temperature has exceeded the configured threshold.

Current Temperature: 38.5°C
Threshold: 35.0°C
Time: 2025-12-29 10:45:30 UTC

⚠️ Action Required: Please check the water temperature monitoring system
```

## Alternative Free Email Services

If you prefer alternatives to Brevo:

### MailerLite
- **Free tier**: 1,000 subscribers, 12,000 emails/month
- **Setup**: Similar to Brevo, get API key from dashboard
- **Requires code changes**: Update `backend/app/services/email_service.py`

### Sender
- **Free tier**: 2,500 subscribers, 15,000 emails/month
- **Setup**: Get API key from Sender dashboard
- **Requires code changes**: Update API endpoint in email service

#### Quick: Use Sender via SMTP (fast)
- Sign up at https://www.sender.net and go to SMTP settings in your Sender account.
- Copy the SMTP host, port, username and password.
- In Vercel (or your `.env`) set these environment variables:
   - `SMTP_HOST` (e.g. smtp.sender.net)
   - `SMTP_PORT` (usually `587`)
   - `SMTP_USER` (your SMTP username)
   - `SMTP_PASS` (your SMTP password)
   - `SMTP_FROM` (optional, e.g. alerts@yourdomain.com)

The backend already supports SMTP fallback: if `BREVO_API_KEY` is not set, the service will try SMTP using the values above. This is the quickest way to get Sender working without code changes.

### SendGrid (Twilio)
- **Free tier**: 100 emails/day
- **Setup**: Get API key from SendGrid dashboard
- **Requires code changes**: Different API format

## Troubleshooting

### Emails Not Sending
1. **Check API key**: Verify `BREVO_API_KEY` is set correctly
2. **Check logs**: Look for error messages in Vercel logs
3. **Verify recipients**: Ensure at least one recipient is added
4. **Check throttling**: If alert was sent recently, wait 15 minutes

### Emails Going to Spam
1. **Sender verification**: Verify your domain in Brevo (optional but recommended)
2. **SPF/DKIM**: Configure email authentication in Brevo settings
3. **From email**: Use a professional from address (not @gmail.com)

### API Key Invalid
1. Regenerate API key in Brevo dashboard
2. Update environment variable in Vercel
3. Redeploy the application

## Alert History

View recent alert history:
- API endpoint: `GET /api/v1/alert-history`
- Returns last 10 TDS and Temperature alerts
- Shows timestamp, value, threshold, and recipients

## Usage Limits (Brevo Free Tier)

- **Daily limit**: 300 emails
- **Monthly limit**: 9,000 emails
- **Contacts**: Up to 100,000 contacts (recipients)
- **No credit card required**

### Calculating Your Usage
With 15-minute throttling per alert type:
- **Maximum TDS alerts/day**: 96 (1 every 15 min × 24 hours)
- **Maximum Temp alerts/day**: 96
- **Total maximum**: 192 emails/day (well within 300 limit)

## Security Notes

- ✅ API key stored as environment variable (never in code)
- ✅ Recipient emails validated before storage
- ✅ No password storage (authentication via existing system)
- ✅ HTTPS encryption for all API calls
- ✅ Rate limiting prevents abuse

## Need Help?

- **Brevo Documentation**: https://developers.brevo.com/
- **Brevo Support**: support@brevo.com
- **Project Issues**: Open an issue on GitHub

---

**© 2025 EvaraTech & IIIT Hyderabad**
