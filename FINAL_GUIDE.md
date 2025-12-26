# ⚡ Ultra-Simple Alert System

## What It Does
- ✅ Sends water quality reports **every 15 minutes** to your Telegram group
- ✅ Shows **TDS level (ppm)** and **temperature**
- ✅ Indicates **Safe** or **Alert** status
- ✅ **No recipient management** - just add people to Telegram group

---

## Setup (2 Steps)

### Step 1: Get Your Chat ID
```powershell
python get_group_chat_id.py
```
Copy the chat ID and update `backend/.env`:
```env
TELEGRAM_ALERT_CHAT_ID=YOUR_CHAT_ID_HERE
```

### Step 2: Start Alerts
```powershell
cd backend
python periodic_alerts.py
```

**That's it!** Alerts will be sent every 15 minutes.

---

## Adding People
Just invite them to your Telegram group using this link:
**https://t.me/+K2URmImZb9tmMDc9**

Everyone in the group gets all alerts automatically.

---

## Alert Format

```
🌊 Water Quality Report - SAFE

✅ Current Readings:
━━━━━━━━━━━━━━━━━━━━
💧 TDS Level: 125.0 ppm ✅
   Threshold: 150 ppm
   Status: Safe

🌡️ Temperature: 28.5°C ✅
   Threshold: 35°C
   Status: Normal

⚡ Voltage: 4.85V
━━━━━━━━━━━━━━━━━━━━

📊 Overall Status: ✅ Safe to Use

Reading Time: 2025-12-26T10:30:00
Next update in 15 minutes
```

---

## Configuration

Edit `backend/.env`:
```env
# Bot (already configured)
TELEGRAM_BOT_TOKEN=8507962260:AAHaRXknIvbEILzEgdK4rJ0rRcMNyV3q2NY

# Where to send alerts
TELEGRAM_ALERT_CHAT_ID=1362954575

# Group invite link
TELEGRAM_GROUP_INVITE_LINK=https://t.me/+K2URmImZb9tmMDc9

# Thresholds
TDS_ALERT_THRESHOLD=150
TEMP_ALERT_THRESHOLD=35
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python periodic_alerts.py` | Start 15-min alerts |
| `python test_simple_system.py` | Test bot connection |
| `python get_group_chat_id.py` | Get chat ID |

---

**That's everything!** Just run `periodic_alerts.py` and invite people to the Telegram group. 🎉
