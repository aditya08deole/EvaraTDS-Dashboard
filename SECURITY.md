# Security Policy

## 🔒 Handling Secrets

**CRITICAL**: This project uses environment variables for all sensitive data. Never commit actual secrets to git.

### Protected Files (Already in .gitignore)
- `backend/.env`
- `frontend/.env`
- `frontend/.env.local`
- `frontend/.env.production`

### Setting Up Your Environment

1. **Backend Setup:**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and add your actual secrets
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   cp .env.example .env.local
   # Edit .env.local and add your actual secrets
   ```

### Required Secrets

#### Telegram Bot Token
- Get from: [@BotFather](https://t.me/BotFather) on Telegram
- Format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
- Used for: Sending alerts via Telegram

#### ThingSpeak Keys
- Get from: [ThingSpeak Dashboard](https://thingspeak.com/)
- Channel ID: Your channel number
- Read API Key: Public read key for your channel

#### Authentication Passwords
- Choose strong passwords for admin and viewer accounts
- Change default passwords immediately
- Use password manager to generate secure passwords

### Vercel Deployment

When deploying to Vercel, add environment variables via:
1. Vercel Dashboard → Project → Settings → Environment Variables
2. Add each variable individually
3. Select all environments (Production, Preview, Development)

**Never include actual secrets in:**
- Git commits
- README files
- Documentation
- Issue reports
- Pull requests

### Reporting Security Issues

If you find a security vulnerability:
1. **DO NOT** open a public issue
2. Email: [your-security-email@example.com]
3. Include detailed description
4. Allow 48 hours for response

## Best Practices

✅ **Do:**
- Use `.env` files for secrets
- Add `.env` to `.gitignore`
- Use environment variables in code
- Rotate secrets regularly
- Use different secrets for dev/prod

❌ **Don't:**
- Hardcode secrets in source code
- Commit `.env` files
- Share secrets in chat/email
- Use same secrets across projects
- Leave default passwords unchanged

## Compromised Secrets

If you accidentally expose secrets:

1. **Immediately revoke/regenerate:**
   - Telegram: Create new bot with @BotFather
   - ThingSpeak: Regenerate API keys
   - Passwords: Change immediately

2. **Update all environments:**
   - Local `.env` files
   - Vercel environment variables
   - Any other deployments

3. **Force push to remove from git history** (if needed):
   ```bash
   # Use with extreme caution - rewrites history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/exposed/file" \
     --prune-empty --tag-name-filter cat -- --all
   ```

## Audit Trail

All security-related changes should be logged here:

- **2025-12-25**: Initial security policy created
- **2025-12-25**: Removed all hardcoded secrets from codebase
- **2025-12-25**: Updated all documentation to use placeholders
