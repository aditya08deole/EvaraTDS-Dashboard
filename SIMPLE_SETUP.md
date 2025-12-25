# Simple Setup - JSON Storage + Periodic Alerts

## Overview
Simplified system with:
- ✅ **JSON storage** (no database needed)
- ✅ **Group invite link configured**: https://t.me/+K2URmImZb9tmMDc9
- ✅ **Periodic alerts every 15 minutes** with TDS/temp readings

---

## Quick Start

### 1. Get Group Chat ID
First, get your Telegram group chat ID where alerts will be sent:

```powershell
python get_group_chat_id.py
```

Copy the chat ID (should be a number like `1362954575` or negative for groups like `-1001234567890`)

### 2. Update .env File
Edit `backend/.env` and set:

```env
TELEGRAM_BOT_TOKEN=8507962260:AAHaRXknIvbEILzEgdK4rJ0rRcMNyV3q2NY
TELEGRAM_ALERT_CHAT_ID=YOUR_CHAT_ID_HERE
TELEGRAM_GROUP_INVITE_LINK=https://t.me/+K2URmImZb9tmMDc9
TDS_ALERT_THRESHOLD=150
TEMP_ALERT_THRESHOLD=35
```

### 3. Start Backend API
```powershell
cd backend
python -m uvicorn main:app --reload
```

Backend runs at: http://localhost:8000

### 4. Start Periodic Alerts (in new terminal)
```powershell
cd backend
python periodic_alerts.py
```

This will:
- Send water quality status every 15 minutes
- Show TDS level (ppm)
- Show temperature (°C)
- Indicate if safe or not

---

## How It Works

### Recipients (JSON Storage)
Recipients are stored in `backend/data/recipients.json`:
```json
[
  {
    "id": 1,
    "name": "Aditya Deole",
    "phone": "+919876543210",
    "is_active": true,
    "channels": ["telegram"],
    "created_at": "2025-12-25T10:30:00"
  }
]
```

### Add Recipients via Dashboard
1. Open http://localhost:5173
2. Go to Alerts page
3. Click "Add Recipient"
4. Enter name and phone number
5. They get the group invite link: https://t.me/+K2URmImZb9tmMDc9

### Periodic Alerts
Every 15 minutes, the system:
1. Fetches latest TDS/temperature from ThingSpeak
2. Checks against thresholds (TDS: 150 ppm, Temp: 35°C)
3. Sends status message to Telegram group:
   - ✅ Safe: TDS < 150, Temp < 35
   - ⚠️ Alert: TDS or Temp exceeds limits
   - Shows current PPM level
   - Shows current temperature

---

## API Endpoints

All recipients and history stored in JSON files:

```bash
# Get recipients
curl http://localhost:8000/api/v1/alerts/recipients

# Add recipient
curl -X POST http://localhost:8000/api/v1/alerts/recipients \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","phone":"+919876543210","role":"viewer"}'

# Delete recipient
curl -X DELETE http://localhost:8000/api/v1/alerts/recipients/1

# Get alert history
curl http://localhost:8000/api/v1/alerts/history

# Get system status
curl http://localhost:8000/api/v1/alerts/status

# Send test alert
curl -X POST http://localhost:8000/api/v1/alerts/test \
  -H "Content-Type: application/json" \
  -d '{"message":"Manual test"}'
```

---

## Files Structure

```
backend/
├── data/
│   ├── recipients.json         # All recipients (auto-created)
│   └── alert_history.json      # Alert logs (auto-created)
├── .env                        # Configuration (YOU EDIT THIS)
├── main.py                     # FastAPI server
├── periodic_alerts.py          # 15-min alert loop
└── app/
    └── api/v1/
        └── alerts_simple.py    # Simple JSON-based API
```

---

## Testing

### Test 1: Manual Alert
```powershell
cd backend
python send_test_alert.py
```
Check Telegram for message!

### Test 2: API Test
```powershell
curl -X POST http://localhost:8000/api/v1/alerts/test \
  -H "Content-Type: application/json" \
  -d '{"message":"API test"}'
```

### Test 3: Add Recipient
```powershell
curl -X POST http://localhost:8000/api/v1/alerts/recipients \
  -H "Content-Type: application/json" \
  -d '{"name":"My Name","phone":"+919876543210","role":"viewer"}'
```

Check `backend/data/recipients.json` - should see your entry!

---

## Troubleshooting

### Bot not sending messages
1. Check TELEGRAM_BOT_TOKEN in .env
2. Check TELEGRAM_ALERT_CHAT_ID is correct
3. Run: `python backend/scripts/verify_bot.py`

### No recipients showing
- Check `backend/data/recipients.json` exists
- If empty, add one via API or dashboard

### Periodic alerts not running
- Make sure `python periodic_alerts.py` is running
- Check console for errors
- Verify ThingSpeak channel is public

---

## Deployment to Vercel

For Vercel (API only):

1. The API will work automatically (uses `/tmp` for JSON on Vercel)
2. Periodic alerts need to run separately (use a cron service or local machine)
3. Set env vars in Vercel dashboard:
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_ALERT_CHAT_ID
   - TELEGRAM_GROUP_INVITE_LINK

---

## Group Invite Link

Already configured: **https://t.me/+K2URmImZb9tmMDc9**

Share this link with people who should receive alerts. Once they join the group, they'll get all periodic updates!

---

**That's it!** No database setup, no Postgres, just simple JSON files. 🎉
