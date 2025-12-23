# Vercel Environment Variables Setup

## Required Environment Variables for Vercel Deployment

After deploying to Vercel, you **MUST** add these environment variables in your Vercel project settings:

### Backend Environment Variables

Go to: **Vercel Dashboard → Your Project → Settings → Environment Variables**

Add the following:

| Variable Name | Value | Environment | Type |
|--------------|-------|-------------|------|
| `THINGSPEAK_CHANNEL_ID` | `2713286` | Production & Preview | Plain Text |
| `THINGSPEAK_READ_KEY` | `EHEK3A1XD48TY98B` | Production & Preview | Secret (Encrypted) |
| `TDS_ALERT_THRESHOLD` | `150.0` | Production & Preview | Plain Text |

### How to Add:

1. Open your Vercel project dashboard
2. Click **Settings** → **Environment Variables**
3. For each variable:
   - **Key**: Enter the variable name (e.g., `THINGSPEAK_CHANNEL_ID`)
   - **Value**: Enter the corresponding value
   - **Environments**: Select both "Production" and "Preview"
   - **For sensitive keys** (like `THINGSPEAK_READ_KEY`): Check "Sensitive" to encrypt the value
4. Click **Save**

### After Adding Variables:

**Important**: Redeploy your application after adding environment variables!

```bash
# Option 1: Push a new commit (triggers auto-deploy)
git commit --allow-empty -m "Trigger redeploy with env vars"
git push origin main

# Option 2: Use Vercel CLI
vercel --prod
```

Or go to: **Deployments → ⋯ (three dots) → Redeploy**

---

## Local Development

For local development, create a `.env` file in the `backend/` directory:

```bash
cp backend/.env.example backend/.env
```

The `.env` file is already configured with the correct values and is ignored by git for security.

---

## Troubleshooting

### If you see 404 or NOT_FOUND errors:
- ✅ Verify all environment variables are set in Vercel
- ✅ Check that you selected "Production & Preview" for all variables
- ✅ Redeploy after adding variables (variables are only loaded at build time)
- ✅ Check deployment logs for any errors related to missing env vars

### If backend fails to fetch data:
- ✅ Verify `THINGSPEAK_CHANNEL_ID` is correct (2713286)
- ✅ Verify `THINGSPEAK_READ_KEY` is correct (EHEK3A1XD48TY98B)
- ✅ Ensure the ThingSpeak channel is accessible

---

**Note**: The values are already hardcoded in `backend/app/core/config.py` as fallbacks, but setting them as environment variables in Vercel is the recommended production practice for security and flexibility.
