# Authentication Setup (Clerk + Google + OTP)

This project uses Clerk for enterprise-grade authentication (Google OAuth + Email/Phone OTP) with secure session handling and onboarding.

## 1) Clerk Dashboard
- Create a Clerk application at https://dashboard.clerk.com
- Enable the following sign-in methods in Settings → Authentication:
  - OAuth: Google
  - Email code
  - Phone code (optional, requires SMS domain verification)

## 2) Environment Variables
Create `frontend/.env` from the example and set the Clerk publishable key.

```
cp frontend/.env.example frontend/.env
```

Then set:

```
VITE_CLERK_PUBLISHABLE_KEY=pk_test_xxx_or_pk_live_xxx
```

On Vercel, add the same variable in Project → Settings → Environment Variables.

## 3) Vercel config
`vercel.json` already includes SPA fallback and Clerk API passthrough. No extra rewrites are required for Clerk.

## 4) Local development
- Start the frontend:

```bash
cd frontend
npm install
npm run dev
```

- Open http://localhost:5173/login to test Sign In (Google/Email/Phone).

## 5) Onboarding Flow
- First-time users are redirected to `/onboarding` after sign-in.
- The page writes `publicMetadata.onboarded = true` and updates the profile name.

## 6) Session & Security
- Clerk stores session in httpOnly + Secure cookies by default.
- Frontend guards use Clerk’s session for route protection.
- For backend APIs, send `Authorization: Bearer <token>` using Clerk’s `getToken()` (future enhancement).

## 7) Google OAuth Notes
- In Clerk → OAuth → Google, set Authorized Redirect URLs to include your domain (Vercel preview + production) and `http://localhost:5173` for local.
- Ensure the domain of your site matches the one configured in Clerk → Domains.

## 8) Phone OTP Notes (optional)
- For SMS, verify a custom domain in Clerk and/or connect Twilio if using custom SMS.
- Enable reCAPTCHA in Clerk if you see bot traffic.

## 9) Troubleshooting
- 404 on auth pages: ensure SPA fallback rewrite exists (present) and `/login` route is defined.
- OAuth blocked by popup: ensure popups/domains aren’t blocked by the browser.
- Environment variable missing: confirm `VITE_CLERK_PUBLISHABLE_KEY` exists at build time on Vercel.
