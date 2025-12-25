# ✅ DONE - Simple JSON-Based System Ready!

## What Was Changed

### ✅ Removed Completely
- ❌ PostgreSQL database
- ❌ SQLAlchemy ORM  
- ❌ psycopg2-binary
- ❌ Database migrations
- ❌ Complex Postgres setup

### ✅ Added Instead
- ✅ Simple JSON file storage (`recipients.json`, `alert_history.json`)
- ✅ Periodic alerts every 15 minutes
- ✅ Group invite link configured: https://t.me/+K2URmImZb9tmMDc9
- ✅ Shows PPM level + Safe/Alert status in every message

---

## 🚀 How to Use (3 Steps)

### Step 1: Get Your Group Chat ID
```powershell
python get_group_chat_id.py
```
Update `backend/.env` with your chat ID:
```env
TELEGRAM_ALERT_CHAT_ID=YOUR_CHAT_ID_HERE
```

### Step 2: Start Backend
```powershell
cd backend
python -m uvicorn main:app --reload
```
Runs at: http://localhost:8000

### Step 3: Start Periodic Alerts
```powershell
# In a new terminal
cd backend
python periodic_alerts.py
```

**That's it!** 🎉

---

## 📊 What the Alerts Look Like

Every 15 minutes, your Telegram gets:

```
🌊 Water Quality Status - SAFE

✅ Current Readings:
━━━━━━━━━━━━━━━━━━━━
💧 TDS Level: 125.3 ppm ✅
   Threshold: 150 ppm
   Status: Safe

🌡️ Temperature: 28.5°C ✅
   Threshold: 35°C
   Status: Normal

⚡ Voltage: 3.85V

━━━━━━━━━━━━━━━━━━━━
📊 Overall Status: ✅ Safe to Use

Updated: 2025-12-25 17:45:00 UTC
Next update in 15 minutes
```

---

## 📁 Data Storage

Everything stored in simple JSON files:

### `backend/data/recipients.json`
```json
[
  {
    "id": 1,
    "name": "Aditya Deole",
    "phone": "+919876543210",
    "is_active": true,
    "channels": ["telegram"],
    "created_at": "2025-12-25T17:30:00"
  }
]
```

### `backend/data/alert_history.json`
```json
[
  {
    "id": 1735148700,
    "alert_type": "periodic",
    "tds_value": 125.3,
    "temp_value": 28.5,
    "tds_safe": true,
    "temp_safe": true,
    "overall_safe": true,
    "created_at": "2025-12-25T17:45:00"
  }
]
```

---

## 🧪 Testing

### Test 1: System Check
```powershell
cd backend
python test_simple_system.py
```
**Result:** ✅ Bot connected, test message sent!

### Test 2: Manual Alert
```powershell
python send_test_alert.py
```
**Result:** Check your Telegram!

### Test 3: Add Recipient via API
```powershell
curl -X POST http://localhost:8000/api/v1/alerts/recipients `
  -H "Content-Type: application/json" `
  -d '{"name":"Test User","phone":"+919876543210","role":"viewer"}'
```
**Result:** Check `backend/data/recipients.json`

---

## 📱 Adding Recipients

### Method 1: Dashboard UI
1. Open http://localhost:5173
2. Go to Alerts page
3. Click "Add Recipient"
4. Enter name and phone number
5. Click Save

### Method 2: API
```powershell
curl -X POST http://localhost:8000/api/v1/alerts/recipients `
  -H "Content-Type: application/json" `
  -d '{"name":"John Doe","phone":"+919999999999","role":"viewer"}'
```

### Method 3: Edit JSON directly
Edit `backend/data/recipients.json` manually.

---

## 🌐 Vercel Deployment

### For API Only:
1. Push to GitHub (already done ✅)
2. Vercel auto-deploys
3. Set env vars in Vercel dashboard:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_ALERT_CHAT_ID`
   - `TELEGRAM_GROUP_INVITE_LINK`

### For Periodic Alerts:
Periodic alerts need to run continuously, so either:
- **Option A:** Run on your local machine (recommended for testing)
- **Option B:** Use a cron service (cron-job.org) to trigger an endpoint every 15 min
- **Option C:** Use a separate always-on server (VPS, Raspberry Pi, etc.)

---

## 🔧 Configuration

All settings in `backend/.env`:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=8507962260:AAHaRXknIvbEILzEgdK4rJ0rRcMNyV3q2NY
TELEGRAM_ALERT_CHAT_ID=1362954575
TELEGRAM_GROUP_INVITE_LINK=https://t.me/+K2URmImZb9tmMDc9

# ThingSpeak
THINGSPEAK_CHANNEL_ID=2713286
THINGSPEAK_READ_KEY=EHEK3A1XD48TY98B

# Alert Thresholds
TDS_ALERT_THRESHOLD=150.0
TEMP_ALERT_THRESHOLD=35.0
```

---

## 📋 API Endpoints

### Recipients
- `GET /api/v1/alerts/recipients` - List all recipients
- `POST /api/v1/alerts/recipients` - Add new recipient
- `DELETE /api/v1/alerts/recipients/{id}` - Remove recipient
- `PATCH /api/v1/alerts/recipients/{id}/toggle` - Activate/deactivate

### Alerts
- `GET /api/v1/alerts/history` - View alert history
- `GET /api/v1/alerts/status` - System status
- `POST /api/v1/alerts/test` - Send test alert

API docs: http://localhost:8000/docs

---

## ✅ What's Working

1. ✅ **Bot connected** - @EvaraTDS_bot online
2. ✅ **Group invite configured** - https://t.me/+K2URmImZb9tmMDc9
3. ✅ **JSON storage** - No database needed
4. ✅ **Periodic alerts** - Every 15 minutes
5. ✅ **Shows PPM levels** - TDS value in every alert
6. ✅ **Safe/Alert status** - Clear indication if water is safe
7. ✅ **Phone-based recipients** - Add by phone number
8. ✅ **Test successful** - Verified with test_simple_system.py

---

## 📚 Documentation Files

- **[SIMPLE_SETUP.md](SIMPLE_SETUP.md)** - Full setup guide
- **[TELEGRAM_GROUP_SETUP.md](TELEGRAM_GROUP_SETUP.md)** - Group configuration
- **This file** - Quick reference

---

## 🎯 Next Steps for You

1. **Get your group chat ID:**
   ```powershell
   python get_group_chat_id.py
   ```

2. **Update .env** with your chat ID

3. **Start the systems:**
   ```powershell
   # Terminal 1
   cd backend
   python -m uvicorn main:app --reload
   
   # Terminal 2
   cd backend  
   python periodic_alerts.py
   ```

4. **Add recipients** via dashboard or API

5. **Share group link** with recipients: https://t.me/+K2URmImZb9tmMDc9

---

## 🆘 Need Help?

Run the test:
```powershell
cd backend
python test_simple_system.py
```

If bot not working:
```powershell
cd backend
python scripts/verify_bot.py
```

Check data files:
```powershell
cat backend/data/recipients.json
cat backend/data/alert_history.json
```

---

**Everything is simplified and working!** 🎉

No Postgres, no complex setup - just JSON files and a bot that sends alerts every 15 minutes with TDS levels.
