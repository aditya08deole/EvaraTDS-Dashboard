# 🔔 Alert System Setup Guide

## Quick Setup (5 Minutes)

### Step 1: Create Telegram Bot

1. Open Telegram → Search **@BotFather**
2. Send `/newbot`
3. Name: `Evara TDS Alert Bot`
4. Username: `evara_tds_bot` (must be unique)
5. **Copy the token** (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Configure Backend

Edit `backend/.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### Step 3: Get Your Chat ID

**Method 1: Browser**
1. Send `/start` to your bot
2. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find: `"chat":{"id":123456789}`

**Method 2: curl**
```bash
curl https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```

### Step 4: Add Recipient

1. Open http://localhost:5173
2. Login (admin: `Aditya.Evaratech` / `[see .env file]`)
3. Go to **Alerts** page
4. Click **Add Recipient**
5. Enter your name and chat ID
6. Click **Add Recipient**

### Step 5: Test

Click **Send Test Alert** button → Check Telegram!

---

## Alert Configuration

### Adjust Thresholds

Click **Configure** button:
- **TDS Threshold** (default: 150 ppm)
- **Warning Threshold** (default: 135 ppm)
- **Cooldown** (default: 15 minutes)

### Cooldown Logic

Prevents spam. Example with 15-min cooldown:
- 10:00 AM - Alert sent ✅
- 10:05 AM - Suppressed (cooldown active)
- 10:20 AM - Alert sent ✅

---

## Message Format

```
🚨 EVARA TDS ALERT 🚨

Alert Type: High TDS
Threshold Exceeded: 150.0

Current Readings:
• TDS: 175.50 ppm
• Temperature: 24.30°C
• Voltage: 4.95V

Timestamp: 2025-12-25 10:30:45
```

---

## Troubleshooting

**"Telegram bot not configured"**
- Check `TELEGRAM_BOT_TOKEN` in `backend/.env`
- Restart backend

**"No active recipients"**
- Add recipient via Alerts page
- Ensure chat ID is numeric

**"Failed to send alert"**
- Verify you sent `/start` to bot
- Check token is correct
- Ensure not blocked

**Alerts not auto-triggering**
- Check threshold isn't too high
- Verify cooldown hasn't activated
- Check alert history

---

## Database

SQLite database: `backend/alerts.db`

### View Data (Optional)
```bash
cd backend
sqlite3 alerts.db
SELECT * FROM alert_recipients;
SELECT * FROM alert_history ORDER BY created_at DESC LIMIT 10;
.quit
```

---

## Production Setup

**Backend (.env):**
```env
TELEGRAM_BOT_TOKEN=your_production_token
TDS_ALERT_THRESHOLD=150.0
ALERT_COOLDOWN_MINUTES=15
DATABASE_URL=sqlite:///./alerts.db
```

**Frontend (.env):**
```env
VITE_API_BASE_URL=https://your-backend-url.railway.app
```

---

**For full documentation, see [README.md](README.md)**

