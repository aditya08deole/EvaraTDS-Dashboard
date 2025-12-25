# 🚀 Quick Reference - Next Steps

## ⚡ Immediate Actions Required

### 1. Create Telegram Group (5 minutes)
```
1. Open Telegram
2. Click "New Group"
3. Name: "Evara TDS Alerts"
4. Add @EvaraTDS_bot
5. Group Settings → Administrators → Add bot
6. Enable "Post Messages" permission
```

### 2. Get Group Chat ID (2 minutes)
```bash
python get_group_chat_id.py
```
**Copy the negative number** (e.g., `-1001234567890`)

### 3. Create Invite Link (1 minute)
```
1. Open group
2. Group Settings → Invite Link
3. Click "Create Link"
4. Copy link (https://t.me/+ABC123xyz)
```

### 4. Update Local Environment (1 minute)
Edit `backend/.env`:
```env
TELEGRAM_GROUP_CHAT_ID=-1001234567890
TELEGRAM_GROUP_INVITE_LINK=https://t.me/+yourLinkHere
```

### 5. Test Locally (1 minute)
```bash
cd backend
python send_test_alert.py
```
✅ Check Telegram group for message!

### 6. Setup Vercel Postgres (3 minutes)
```bash
vercel postgres create evara-tds-db
vercel env add TELEGRAM_GROUP_CHAT_ID
# Enter: -1001234567890
vercel env add TELEGRAM_GROUP_INVITE_LINK
# Enter: https://t.me/+yourLinkHere
vercel env pull
```

### 7. Deploy to Production (2 minutes)
```bash
git push origin main
# Auto-deploys to Vercel
```

---

## 📋 Checklist

- [ ] Telegram group created
- [ ] Bot added to group as admin
- [ ] Group chat ID obtained (negative number)
- [ ] Invite link created
- [ ] Local .env updated
- [ ] Test alert sent locally (successful)
- [ ] Vercel Postgres created
- [ ] Vercel env vars added (GROUP_CHAT_ID, INVITE_LINK)
- [ ] Pushed to GitHub
- [ ] Verified deployment on Vercel
- [ ] Test alert sent from production

---

## 🧪 Testing Commands

```bash
# Test bot connection
curl https://api.telegram.org/bot8507962260:AAHaRXknIvbEILzEgdK4rJ0rRcMNyV3q2NY/getMe

# Get updates (see group messages)
curl https://api.telegram.org/bot8507962260:AAHaRXknIvbEILzEgdK4rJ0rRcMNyV3q2NY/getUpdates

# Local test alert
cd backend && python send_test_alert.py

# Add test recipient
curl -X POST http://localhost:8000/api/v1/alerts/recipients \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","phone":"+919876543210","role":"viewer"}'

# Production test (replace URL)
curl -X POST https://your-app.vercel.app/api/v1/alerts/test \
  -H "Content-Type: application/json" \
  -d '{"message":"Production test"}'
```

---

## 🔧 Troubleshooting

### Bot not sending to group
```bash
# Check bot is admin
# Check TELEGRAM_GROUP_CHAT_ID is negative
# Check bot has "Post Messages" permission
```

### Can't add recipients on Vercel
```bash
# Create Postgres database first
vercel postgres create evara-tds-db

# Pull env vars
vercel env pull

# Redeploy
git push origin main
```

### Configure button not working
**Temporary workaround:**
```bash
# Update thresholds via API
curl -X PUT https://your-app.vercel.app/api/v1/alerts/config \
  -H "Content-Type: application/json" \
  -d '{"tds_threshold":150,"warning_threshold":120,"cooldown_minutes":15,"enable_telegram":true}'
```

---

## 📱 Current System Status

| Component | Status | Notes |
|-----------|--------|-------|
| Telegram Bot | ✅ Working | @EvaraTDS_bot configured |
| Local Testing | ✅ Working | Test alerts successful |
| Phone System | ✅ Ready | Code deployed, needs env vars |
| Postgres | ⏳ Pending | Need to create database |
| Group Alerts | ⏳ Pending | Need group chat ID |
| Vercel Deploy | ⏳ Pending | Need env vars + Postgres |

---

## 📚 Documentation Map

- **Start Here:** [TELEGRAM_GROUP_SETUP.md](TELEGRAM_GROUP_SETUP.md)
- **Changes:** [CHANGES.md](CHANGES.md)
- **Quick Setup:** [QUICK_SETUP.md](QUICK_SETUP.md)
- **Security:** [SECURITY.md](SECURITY.md)
- **Overview:** [README.md](README.md)

---

## ⏱️ Estimated Time to Production

**Total:** ~15 minutes

1. Telegram setup: 5 min
2. Get chat ID: 2 min
3. Local config: 1 min
4. Local test: 1 min
5. Vercel Postgres: 3 min
6. Deploy: 2 min
7. Production test: 1 min

---

## 🎯 Success Criteria

You'll know it's working when:
- ✅ Test alert appears in Telegram group
- ✅ Can add recipients from Vercel dashboard
- ✅ Recipients show phone numbers in table
- ✅ Bot status shows "Configured"
- ✅ No errors in Vercel logs

---

## 💡 Pro Tips

1. **Test locally first** - Verify everything works before deploying
2. **Keep .env secret** - Already in .gitignore, never commit
3. **Group invite link** - Share with new recipients manually until SMS integrated
4. **Bot permissions** - Must be admin with "Post Messages"
5. **Phone format** - Always use +91 prefix for India

---

## 🆘 Quick Help

**Bot not responding?**
```bash
python backend/scripts/verify_bot.py
```

**Database issues?**
```bash
vercel postgres list
vercel logs
```

**Need group chat ID again?**
```bash
python get_group_chat_id.py
```

---

**Ready? Start with [TELEGRAM_GROUP_SETUP.md](TELEGRAM_GROUP_SETUP.md)** 🚀
