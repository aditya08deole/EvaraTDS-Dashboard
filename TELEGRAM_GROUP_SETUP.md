# Telegram Group Setup Guide

## Overview
The simplified alert system sends all alerts to a **single Telegram group** instead of managing individual chat IDs. Recipients join the group via invite links.

## Why Group-Based Alerts?
✅ **Simpler**: No need to collect individual chat IDs  
✅ **Scalable**: Add unlimited recipients easily  
✅ **Better UX**: Recipients join with one click  
✅ **Production-Ready**: Works on Vercel (no database issues)

---

## Step 1: Create Telegram Group

1. **Open Telegram** on your phone or desktop
2. **Create New Group**:
   - Click **New Group** or **New Channel**
   - Name it: "Evara TDS Alerts" (or your preferred name)
   - Add a description: "Automated water quality alerts from Evara TDS platform"
3. **Add Your Bot**:
   - Click "Add Members"
   - Search for: `@EvaraTDS_bot`
   - Add the bot to the group
4. **Make Bot Admin**:
   - Go to Group Settings → Administrators
   - Add `@EvaraTDS_bot` as admin
   - Enable **"Post Messages"** permission
   - ✅ Save

---

## Step 2: Get Group Chat ID

### Method 1: Using getUpdates API
1. **Send a message** in your newly created group (any text)
2. **Open this URL** in your browser:
   ```
   https://api.telegram.org/bot8507962260:AAHaRXknIvbEILzEgdK4rJ0rRcMNyV3q2NY/getUpdates
   ```
3. **Look for your message** in the JSON response
4. **Find the chat ID**:
   ```json
   {
     "message": {
       "chat": {
         "id": -1001234567890,  ← This is your group chat ID
         "title": "Evara TDS Alerts",
         "type": "supergroup"
       }
     }
   }
   ```
5. **Copy the negative number** (e.g., `-1001234567890`)

### Method 2: Using a Bot (Easier)
1. Add **@userinfobot** to your group
2. The bot will automatically reply with the chat ID
3. Remove the bot after getting the ID

---

## Step 3: Create Invite Link

1. **Open Group Settings**
2. **Click "Invite Link"** or **"Invite via Link"**
3. **Create a new invite link**:
   - Option A: Click "Create Link" for a permanent link
   - Option B: Set expiration/member limit if needed
4. **Copy the link** (format: `https://t.me/+ABC123xyz`)

---

## Step 4: Update Environment Variables

### For Local Development:
Edit `backend/.env`:
```env
# Add these lines:
TELEGRAM_GROUP_CHAT_ID=-1001234567890
TELEGRAM_GROUP_INVITE_LINK=https://t.me/+yourInviteLinkHere
```

### For Vercel Deployment:
1. **Go to Vercel Dashboard** → Your Project → Settings → Environment Variables
2. **Add two new variables**:
   - **Name**: `TELEGRAM_GROUP_CHAT_ID`  
     **Value**: `-1001234567890` (your group chat ID)
   
   - **Name**: `TELEGRAM_GROUP_INVITE_LINK`  
     **Value**: `https://t.me/+yourInviteLinkHere`

3. **Click Save**
4. **Redeploy** your project:
   ```bash
   vercel --prod
   ```

---

## Step 5: Test the System

### Test 1: Send Alert to Group
```bash
cd backend
python send_test_alert.py
```

**Expected**: Message appears in your Telegram group

### Test 2: Add Recipient with Phone
```bash
curl -X POST https://your-api.vercel.app/api/v1/alerts/recipients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "phone": "+919876543210",
    "role": "viewer",
    "is_active": true,
    "channels": ["telegram"]
  }'
```

**Expected**: 
- Recipient added to database
- (Future) SMS/Telegram invite sent with group link

---

## How It Works Now

### Adding Recipients:
1. Admin enters **phone number** in dashboard (e.g., `+919876543210`)
2. System stores recipient in database
3. *(Future)* System sends invite link via SMS or Telegram
4. User clicks link → Joins group
5. User receives all alerts automatically

### Sending Alerts:
- When TDS/temp exceeds threshold → Bot sends **ONE message to group**
- All group members receive the alert
- No need to manage individual chat IDs

---

## Current Status

✅ **Completed**:
- Phone-based recipient system
- Group alert functionality
- Postgres database integration
- Simplified API

⏳ **Pending**:
- Vercel Postgres setup (you need to run: `vercel postgres create`)
- Group chat ID configuration
- SMS integration for automatic invites

🔧 **To Fix**:
- Configure button not working
- Bot status display

---

## Quick Commands Reference

```bash
# Test local alert
python backend/send_test_alert.py

# Add recipient locally
python backend/quick_add_recipient.py

# Check bot status
curl https://your-api.vercel.app/api/v1/alerts/status

# Get bot info (verify connection)
curl -X GET \
  "https://api.telegram.org/bot8507962260:AAHaRXknIvbEILzEgdK4rJ0rRcMNyV3q2NY/getMe"
```

---

## Troubleshooting

### Bot not sending to group
- ✅ Check bot is **admin** in group
- ✅ Verify **TELEGRAM_GROUP_CHAT_ID** is negative number
- ✅ Ensure bot has **"Post Messages"** permission

### Recipients can't be added
- ✅ Check Vercel Postgres is created and connected
- ✅ Verify DATABASE_URL environment variable
- ✅ Check API logs: `vercel logs`

### Invite links not working
- ✅ Verify TELEGRAM_GROUP_INVITE_LINK is set
- ✅ Check link hasn't expired
- ✅ SMS service not yet integrated (manual sharing for now)

---

## Next Steps

1. **Create Telegram group** (5 minutes)
2. **Get group chat ID** using getUpdates (2 minutes)
3. **Add to Vercel env vars** (2 minutes)
4. **Redeploy** (1 minute)
5. **Test alert** (1 minute)
6. **Share invite link** manually until SMS is integrated

**Total Setup Time: ~10 minutes** 🚀

---

## Security Note

- ✅ Bot token: **Secret** (never exposed)
- ✅ Group chat ID: **Not secret** (just a group identifier)
- ✅ Invite link: **Share with recipients** (that's the point!)
- ❌ Never commit `.env` file to GitHub

---

Need help? Check the main [README.md](README.md) or [QUICK_SETUP.md](QUICK_SETUP.md)
