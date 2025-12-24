# 🚀 Vercel Deployment Guide - EvaraTDS Dashboard

## ✅ Environment Variables Setup

Go to **Vercel Dashboard → Your Project → Settings → Environment Variables** and add:

### Required Variables:
```
THINGSPEAK_CHANNEL_ID=2713286
THINGSPEAK_READ_KEY=EHEK3A1XD48TY98B
TDS_ALERT_THRESHOLD=150.0
```

**Important:** Set these for **Production**, **Preview**, and **Development** environments.

---

## 📋 Build Configuration

In Vercel Project Settings → General → Build & Development Settings:

- **Framework Preset:** Other
- **Build Command:** `cd frontend && npm run build`
- **Output Directory:** `frontend/dist`
- **Install Command:** `cd frontend && npm install`
- **Root Directory:** `.` (leave as root)

---

## 🔧 What This Deployment Includes

### Frontend (React + Vite)
- ✅ SPA routing with proper rewrites
- ✅ Assets served from root
- ✅ All client-side routes work (`/dashboard`, `/settings`, etc.)

### Backend API (FastAPI Serverless)
- ✅ Runs as serverless function at `/api/*`
- ✅ ThingSpeak integration for real-time data
- ✅ CORS configured for all origins

---

## 🐛 Troubleshooting

### Issue: 404 on routes like `/dashboard`
**Solution:** Vercel.json includes rewrites to handle SPA routing. Redeploy if you just added it.

### Issue: No data showing / Empty graphs
**Check:**
1. Browser Console (F12) for API errors
2. Verify environment variables are set in Vercel
3. Check Network tab - API calls should go to `/api/v1/dashboard`

### Issue: API calls failing
**Check:**
1. ThingSpeak channel is public or read key is correct
2. CORS errors in browser console
3. Vercel function logs for backend errors

---

## 🎯 Post-Deployment Checklist

- [ ] Environment variables set in Vercel
- [ ] Build succeeds without errors
- [ ] Homepage loads successfully
- [ ] Can navigate to `/dashboard` and `/settings`
- [ ] Graphs show real-time data
- [ ] Works on different devices

---

## 📱 Testing URLs

After deployment, test these URLs:
- `https://your-app.vercel.app/` → Should redirect to dashboard
- `https://your-app.vercel.app/dashboard` → Main dashboard
- `https://your-app.vercel.app/settings` → Settings page
- `https://your-app.vercel.app/api/v1/dashboard` → JSON API response

---

## 🔐 Security Notes

- ThingSpeak credentials are in environment variables
- Never commit `.env` files to git
- CORS is currently set to `*` for development - restrict in production
