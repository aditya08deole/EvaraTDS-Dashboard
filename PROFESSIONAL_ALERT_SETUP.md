# Professional Email Alert Setup Guide (IFTTT + SMTP)

## Overview
EvaraTDS now uses a **professional dual-method alert system**:
1. **IFTTT Webhooks** (Primary) - Fast, reliable, no SMTP setup needed
2. **SMTP** (Fallback) - Activates if IFTTT unavailable
3. **SQLite Database** - Stores recipients and alert logs professionally

## Quick Setup (5 minutes)

### Option 1: IFTTT Webhooks (Recommended - Easiest)

#### Step 1: Get IFTTT Webhook Key
1. Sign up at https://ifttt.com (free account)
2. Go to https://ifttt.com/maker_webhooks
3. Click **Settings** → Copy your webhook key

#### Step 2: Create IFTTT Applets
**For TDS Alerts:**
1. Go to https://ifttt.com/create
2. **If This**: Choose "Webhooks" → "Receive a web request"
   - Event name: `evara_tds_alert`
3. **Then That**: Choose "Email" → "Send me an email"
   - Subject: `🚨 TDS Alert: {{Value1}}`
   - Body: `{{Value1}}<br>{{Value2}}<br>Recipients: {{Value3}}`
4. Click **Finish**

**For Temperature Alerts:**
1. Create another applet
2. **If This**: Webhooks → Event name: `evara_temp_alert`
3. **Then That**: Email (same as above)

#### Step 3: Configure Environment Variables
**Vercel (Production):**
- Go to Project → Settings → Environment Variables
- Add:
  ```
  IFTTT_WEBHOOK_KEY=your_webhook_key_here
  IFTTT_EVENT_TDS=evara_tds_alert
  IFTTT_EVENT_TEMP=evara_temp_alert
  ```

**Local (.env file):**
```bash
# backend/.env
IFTTT_WEBHOOK_KEY=your_webhook_key_here
IFTTT_EVENT_TDS=evara_tds_alert
IFTTT_EVENT_TEMP=evara_temp_alert
```

---

### Option 2: SMTP Fallback (Gmail Example)

#### Step 1: Get Gmail App Password
1. Enable 2-Step Verification on Google Account
2. Go to: https://myaccount.google.com/apppasswords
3. Select "Mail" → "Other" → Name: "EvaraTDS"
4. Copy the 16-character password

#### Step 2: Configure SMTP Variables
**Vercel:**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASS=your_16_char_app_password
SMTP_FROM=your@gmail.com
```

**Local:**
```bash
# backend/.env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASS=your_16_char_app_password
SMTP_FROM=your@gmail.com
```

---

## How It Works

### Alert Flow
```
1. Dashboard calls POST /api/v1/check-alerts every 60 seconds
2. Backend fetches latest ThingSpeak sensor data
3. Compares TDS/Temp against thresholds in settings.json
4. If exceeded:
   a. Check database: Was alert sent in last 15 minutes? (throttle)
   b. If no: Try IFTTT webhook → If fails: Try SMTP
   c. Log result to SQLite database
5. Recipients get email via IFTTT or SMTP
```

### Database Schema
**Recipients Table:**
- id (UUID primary key)
- name, email (unique)
- added_at (timestamp)
- is_active (1=active, 0=deleted)

**Alert Logs Table:**
- id (auto-increment)
- alert_type (tds/temp)
- value, threshold
- recipients (JSON array)
- sent_at, method (ifttt/smtp)
- status (success/failed)

---

## API Endpoints

### Recipients Management
```bash
# Get all active recipients
GET /api/v1/recipients

# Add new recipient
POST /api/v1/recipients
Body: {"name": "John", "email": "john@example.com"}

# Delete recipient (soft delete)
DELETE /api/v1/recipients/{id}
```

### Alert Management
```bash
# Trigger manual alert check
POST /api/v1/check-alerts

# Get recent alert history
GET /api/v1/alert-history?limit=10
```

---

## Testing Locally

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Create .env File
```bash
# backend/.env
IFTTT_WEBHOOK_KEY=your_key_here
IFTTT_EVENT_TDS=evara_tds_alert
IFTTT_EVENT_TEMP=evara_temp_alert
```

### 3. Run Backend
```bash
uvicorn app.index:app --reload --port 8000
```

### 4. Add Recipient
```bash
curl -X POST http://localhost:8000/api/v1/recipients \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"you@example.com"}'
```

### 5. Trigger Test Alert
```bash
curl -X POST http://localhost:8000/api/v1/check-alerts
```

### 6. Check Logs
```bash
curl http://localhost:8000/api/v1/alert-history
```

---

## Configuration Options

### Environment Variables
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `IFTTT_WEBHOOK_KEY` | IFTTT webhook key | - | Recommended |
| `IFTTT_EVENT_TDS` | TDS event name | evara_tds_alert | No |
| `IFTTT_EVENT_TEMP` | Temp event name | evara_temp_alert | No |
| `SMTP_HOST` | SMTP server | - | For fallback |
| `SMTP_PORT` | SMTP port | 587 | No |
| `SMTP_USER` | SMTP username | - | For fallback |
| `SMTP_PASS` | SMTP password | - | For fallback |
| `SMTP_FROM` | From email | alerts@evaratds.com | No |
| `ALERT_THROTTLE_MINUTES` | Throttle time | 15 | No |

### Throttle Settings
- Default: 15 minutes per alert type
- Customizable via `ALERT_THROTTLE_MINUTES` env var
- TDS and Temperature tracked separately
- Prevents spam during sustained threshold exceedance

---

## IFTTT vs SMTP Comparison

| Feature | IFTTT | SMTP (Gmail) | SMTP (Sender) |
|---------|-------|--------------|---------------|
| Setup Time | ⭐⭐⭐⭐⭐ 2 min | ⭐⭐⭐⭐ 5 min | ⭐⭐⭐⭐ 5 min |
| Free Tier | 3 applets | ~500/day | 15K/month |
| Reliability | ⭐⭐⭐⭐ High | ⭐⭐⭐ Medium | ⭐⭐⭐⭐ High |
| Latency | 0-3 sec | 1-5 sec | 1-5 sec |
| Customization | ⭐⭐ Basic | ⭐⭐⭐⭐⭐ Full | ⭐⭐⭐⭐⭐ Full |
| Recommended | ✅ Yes | For testing | For production |

---

## Troubleshooting

### IFTTT Not Working
- Check webhook key is correct in env vars
- Verify applet is enabled at https://ifttt.com/my_applets
- Check event names match exactly
- Test webhook manually: https://maker.ifttt.com/trigger/{event}/with/key/{key}

### SMTP Not Working
- Gmail: Check app password, not regular password
- Verify 2FA enabled on Google account
- Check SMTP_HOST, SMTP_PORT correct
- Test credentials with email client first

### No Alerts Sent
- Check recipients exist: `GET /api/v1/recipients`
- Verify thresholds exceeded: Check ThingSpeak data
- Check throttle: Wait 15+ minutes since last alert
- View logs: `GET /api/v1/alert-history`

### Database Issues
- Database auto-creates at `backend/data/evara_alerts.db`
- Check file permissions if errors
- Delete database to reset (will lose history)

---

## Security Best Practices

✅ **DO:**
- Use environment variables for all keys
- Enable 2FA on email accounts
- Use app passwords, not account passwords
- Rotate keys if compromised
- Keep `.env` in `.gitignore`

❌ **DON'T:**
- Commit API keys to git
- Share webhook keys publicly
- Use personal email passwords
- Disable throttling (spam risk)

---

## Production Deployment Checklist

- [ ] IFTTT webhook key added to Vercel env vars
- [ ] SMTP credentials added as fallback (optional)
- [ ] At least one recipient added via UI
- [ ] Thresholds configured in Settings page
- [ ] Test alert triggered and received
- [ ] Alert history shows successful sends
- [ ] Database file has correct permissions
- [ ] Logs show no errors

---

**© 2025 EvaraTech & IIIT Hyderabad**
