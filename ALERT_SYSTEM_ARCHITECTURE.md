# Alert System Architecture - EvaraTDS Platform
**Author:** System Architect | **Date:** December 25, 2025  
**Priority:** High | **Complexity:** Medium | **Status:** Planning Phase

---

## Executive Summary
Design and implement a real-time alert notification system for TDS threshold breaches with multi-channel delivery (Telegram, Email, SMS) and configurable recipient management.

---

## 1. System Requirements Analysis

### 1.1 Core Requirements
- ✅ **Real-time Monitoring**: Detect TDS threshold breaches within 1-2 seconds
- ✅ **Multi-Channel Delivery**: Telegram (primary), Email (backup), SMS (optional)
- ✅ **Role-Based Access**: Admin configures, Viewers can subscribe
- ✅ **Cost-Effective**: Leverage free tiers and open-source solutions
- ✅ **Reliability**: 99.9% delivery rate with fallback mechanisms
- ✅ **Scalability**: Support 1-100 recipients without performance degradation

### 1.2 Alert Triggers
1. **Critical Alert**: TDS > threshold (default: 150 PPM)
2. **Warning Alert**: TDS approaching threshold (90% of limit)
3. **System Offline**: No data received for 5 minutes
4. **Recovery Alert**: TDS returns to normal after breach

### 1.3 Alert Cooldown
- Prevent spam: Maximum 1 alert per recipient per 5 minutes
- Emergency override: Critical alerts always send

---

## 2. Technology Stack Recommendation

### 2.1 Notification Channels (Ranked by Priority)

#### **Option 1: Telegram Bot (RECOMMENDED) ⭐**
**Why Choose This:**
- ✅ **100% Free** - No API costs, unlimited messages
- ✅ **Instant Delivery** - Push notifications to mobile/desktop
- ✅ **Easy Setup** - 5 minutes to create bot via BotFather
- ✅ **Rich Features** - Support for buttons, images, formatting
- ✅ **Global Reach** - Works worldwide without SMS carrier restrictions
- ✅ **Group Support** - Can send to individual users or groups

**Technical Details:**
```
API: Telegram Bot API (https://core.telegram.org/bots/api)
SDK: node-telegram-bot-api (npm package)
Cost: $0 forever
Rate Limit: 30 messages/second (more than enough)
Setup Time: 5 minutes
```

**Implementation Steps:**
1. Create bot via @BotFather on Telegram
2. Get Bot Token (e.g., `110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`)
3. Users send `/start` to bot to register their Chat ID
4. Backend sends alerts via `sendMessage` API call

#### **Option 2: Email Alerts (BACKUP)**
**Why Include This:**
- ✅ **Universal** - Everyone has email
- ✅ **Free** - Use your domain email or Gmail SMTP
- ✅ **Professional** - HTML formatted alerts with charts
- ✅ **Audit Trail** - Permanent record of all alerts

**Technical Details:**
```
Service: Resend (https://resend.com) or SendGrid
Free Tier: 3,000 emails/month (Resend)
Setup Time: 10 minutes
Cost: $0 for <3k emails/month
```

#### **Option 3: SMS via Twilio (OPTIONAL - PAID)**
**When to Use:**
- Critical infrastructure requiring SMS fallback
- Regulatory compliance (some industries require SMS)
- Recipients without Telegram

**Technical Details:**
```
Service: Twilio
Cost: $0.0079/SMS (India), $0.0075/SMS (USA)
Free Trial: $15 credit (~1,875 SMS)
Monthly Estimate: 100 alerts/month = $0.75
```

**Decision:** Skip SMS unless you have budget or regulatory requirements.

---

## 3. System Architecture

### 3.1 Component Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    EVARA TDS PLATFORM                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND DASHBOARD                         │
│  • Real-time TDS display (1-sec polling)                    │
│  • Alert configuration UI (Admin only)                      │
│  • Recipient management (Add/Remove/Test)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ API Calls
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND API (FastAPI)                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Alert Engine (New Component)                      │    │
│  │  • Threshold monitoring                            │    │
│  │  • Cooldown logic                                  │    │
│  │  • Multi-channel dispatcher                        │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Notification Services                             │    │
│  │  • TelegramService (primary)                       │    │
│  │  • EmailService (backup)                           │    │
│  │  • SMSService (optional)                           │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA STORAGE                            │
│  • Recipients DB (SQLite/PostgreSQL)                        │
│  • Alert History (last 1000 alerts)                         │
│  • Configuration (thresholds, cooldown)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                          │
│  • Telegram Bot API (free)                                  │
│  • Resend/SendGrid (email, free tier)                      │
│  • Twilio (SMS, optional, paid)                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow
```
1. ThingSpeak → Backend → Latest TDS value (every 1 sec)
2. Backend → Alert Engine → Check threshold
3. If breach detected:
   a. Check cooldown (prevent spam)
   b. Format alert message
   c. Send to all recipients via Telegram
   d. Log alert to database
   e. Update dashboard UI (show alert banner)
```

---

## 4. Database Schema

### 4.1 Recipients Table
```sql
CREATE TABLE alert_recipients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    telegram_chat_id VARCHAR(50) UNIQUE,
    email VARCHAR(100),
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'viewer',  -- 'admin' or 'viewer'
    is_active BOOLEAN DEFAULT TRUE,
    channels JSON,  -- ["telegram", "email", "sms"]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);
```

### 4.2 Alert History Table
```sql
CREATE TABLE alert_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type VARCHAR(20),  -- 'critical', 'warning', 'recovery'
    tds_value FLOAT NOT NULL,
    threshold FLOAT NOT NULL,
    message TEXT,
    recipients_notified JSON,  -- ["user1", "user2"]
    channels_used JSON,  -- ["telegram", "email"]
    delivery_status JSON,  -- {"telegram": "success", "email": "pending"}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.3 Alert Configuration Table
```sql
CREATE TABLE alert_config (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

-- Default values:
-- ('tds_threshold', '150')
-- ('warning_threshold', '135')  -- 90% of critical
-- ('cooldown_minutes', '5')
-- ('telegram_bot_token', 'YOUR_BOT_TOKEN')
-- ('enable_email_alerts', 'true')
-- ('enable_sms_alerts', 'false')
```

---

## 5. Alert Message Templates

### 5.1 Critical Alert (Telegram)
```
🚨 CRITICAL ALERT - EvaraTDS

⚠️ HIGH TDS DETECTED
Current: 187 PPM
Threshold: 150 PPM
Status: CRITICAL

📍 Location: ESP32-NODE-01
🕐 Time: 2025-12-25 14:32:15 IST
📊 Trend: Increasing

🔧 ACTION REQUIRED:
Inspect filtration system immediately.

🔗 View Dashboard:
https://evara-tds.vercel.app/dashboard

Powered by EvaraTech
```

### 5.2 Recovery Alert
```
✅ SYSTEM RECOVERED - EvaraTDS

🎉 TDS BACK TO NORMAL
Current: 142 PPM
Threshold: 150 PPM
Status: SAFE

Duration: 15 minutes
Peak: 187 PPM

📍 Location: ESP32-NODE-01
🕐 Time: 2025-12-25 14:47:22 IST

No further action needed.
```

### 5.3 Warning Alert (90% of threshold)
```
⚠️ WARNING - EvaraTDS

TDS Approaching Threshold
Current: 138 PPM (92%)
Threshold: 150 PPM
Status: WARNING

Monitor closely. System may trigger
critical alert soon.

📍 Location: ESP32-NODE-01
🕐 Time: 2025-12-25 14:20:10 IST
```

---

## 6. Implementation Phases

### Phase 1: Backend Foundation (2-3 hours)
**Tasks:**
1. Create database tables for recipients, alerts, config
2. Build Alert Engine class with threshold monitoring
3. Implement cooldown logic (prevent alert spam)
4. Add FastAPI endpoints:
   - `POST /api/alerts/recipients` - Add recipient
   - `GET /api/alerts/recipients` - List all
   - `DELETE /api/alerts/recipients/{id}` - Remove
   - `POST /api/alerts/test` - Send test alert
   - `GET /api/alerts/history` - View past alerts

**Files to Create:**
- `backend/app/services/alert_engine.py`
- `backend/app/services/telegram_service.py`
- `backend/app/services/email_service.py`
- `backend/app/api/v1/alerts.py`
- `backend/app/models/alert.py`
- `backend/database.db` (SQLite)

### Phase 2: Telegram Integration (1 hour)
**Tasks:**
1. Create Telegram bot via @BotFather
2. Implement TelegramService class
3. Add `/start` command handler for user registration
4. Test message delivery
5. Add rich formatting (emojis, buttons)

**Bot Commands:**
- `/start` - Register for alerts
- `/stop` - Unsubscribe from alerts
- `/status` - Check current TDS
- `/history` - View recent alerts

### Phase 3: Frontend UI (2 hours)
**Tasks:**
1. Create Alert Management page (Admin only)
2. Add recipient list with Add/Edit/Delete
3. Build test alert button
4. Show alert history table
5. Add configuration panel (thresholds, cooldown)
6. Real-time alert banner on dashboard

**New Files:**
- `frontend/src/pages/Alerts.tsx`
- `frontend/src/components/AlertBanner.tsx`
- `frontend/src/components/RecipientManager.tsx`
- `frontend/src/services/AlertService.ts`

### Phase 4: Testing & Deployment (1 hour)
**Tasks:**
1. End-to-end testing with real ThingSpeak data
2. Test alert delivery to multiple recipients
3. Verify cooldown logic prevents spam
4. Load testing (simulate 100 alerts/minute)
5. Deploy to Vercel (frontend) + Railway/Render (backend)

### Phase 5: Documentation (30 minutes)
**Tasks:**
1. User guide for recipient registration
2. Admin guide for configuration
3. API documentation
4. Troubleshooting guide

---

## 7. Configuration Management

### 7.1 Admin Dashboard Settings
```typescript
interface AlertSettings {
  tdsThreshold: number;          // 150 PPM
  warningThreshold: number;      // 135 PPM (90% of critical)
  cooldownMinutes: number;       // 5 minutes
  enableTelegram: boolean;       // true
  enableEmail: boolean;          // true
  enableSMS: boolean;            // false
  telegramBotToken: string;      // Hidden in UI, set via env
  emailFrom: string;             // alerts@evaratds.com
  offlineThresholdMinutes: number; // 5 minutes
}
```

### 7.2 Recipient Management UI
```typescript
interface Recipient {
  id: number;
  name: string;
  telegramChatId?: string;  // From /start command
  email?: string;
  phone?: string;
  role: 'admin' | 'viewer';
  isActive: boolean;
  channels: ('telegram' | 'email' | 'sms')[];
  createdAt: Date;
}
```

---

## 8. Security Considerations

### 8.1 Access Control
- ✅ Only **Admins** can add/remove recipients
- ✅ Only **Admins** can modify alert thresholds
- ✅ **Viewers** can only subscribe/unsubscribe themselves
- ✅ Bot token stored in environment variables (never in code)

### 8.2 Rate Limiting
- ✅ Max 10 API calls per minute per IP (prevent abuse)
- ✅ Alert cooldown per recipient (prevent spam)
- ✅ Daily limit: 500 alerts max (safety cap)

### 8.3 Data Privacy
- ✅ Telegram Chat IDs are not publicly visible
- ✅ Phone numbers masked in UI (show last 4 digits only)
- ✅ Alert history auto-purged after 30 days

---

## 9. Cost Analysis

### 9.1 Monthly Cost Breakdown (100 Alerts/Month)
```
Service              Free Tier         Cost (If Exceeded)
─────────────────────────────────────────────────────────
Telegram Bot         Unlimited         $0.00
Resend (Email)       3,000/month       $0.00 (well within)
Twilio (SMS)         $15 trial         $0.75/month (optional)
Backend Hosting      500MB RAM         $0.00 (Railway free tier)
Database (SQLite)    Local file        $0.00
─────────────────────────────────────────────────────────
TOTAL MONTHLY COST                     $0.00 - $0.75
```

### 9.2 Cost at Scale (1000 Alerts/Month)
```
Telegram:            Still free        $0.00
Email:               Still free        $0.00
SMS (if enabled):    1000 × $0.0079   $7.90
Backend:             Upgrade needed    $5.00 (Railway Starter)
─────────────────────────────────────────────────────────
TOTAL                                  $12.90 (with SMS)
                                       $5.00 (Telegram only)
```

**Recommendation:** Start with Telegram-only (100% free), add SMS later if needed.

---

## 10. Rollout Plan

### 10.1 MVP (Minimum Viable Product) - Week 1
**Scope:**
- ✅ Telegram bot setup
- ✅ Single admin recipient
- ✅ Critical alerts only (TDS > 150 PPM)
- ✅ Manual testing

**Goal:** Prove the concept works end-to-end.

### 10.2 Beta Release - Week 2
**Scope:**
- ✅ Multiple recipients support
- ✅ Admin UI for recipient management
- ✅ Warning alerts (90% threshold)
- ✅ Email backup channel
- ✅ Alert history page

**Goal:** Test with 3-5 users, gather feedback.

### 10.3 Production Release - Week 3
**Scope:**
- ✅ Full RBAC (Admin vs Viewer roles)
- ✅ Recovery alerts
- ✅ Offline detection alerts
- ✅ Rich Telegram formatting
- ✅ Comprehensive testing

**Goal:** Launch to all users.

### 10.4 Future Enhancements (Post-Launch)
- 📊 Alert analytics dashboard (trends, response times)
- 🔔 Custom alert rules (e.g., "if TDS > 200 for 10 mins")
- 🌐 WhatsApp Business API integration (requires approval)
- 📞 Voice call alerts for critical failures (Twilio)
- 🤖 AI-powered anomaly detection (predict breaches)
- 📱 Native mobile app with push notifications

---

## 11. Key Decision Matrix

| Question | Decision | Rationale |
|----------|----------|-----------|
| **Should we add alerts?** | ✅ **YES** | Critical for proactive monitoring; industry standard |
| **Which channel is primary?** | **Telegram** | Free, instant, easy setup, global reach |
| **Do we need SMS?** | ❌ **NO** (for now) | Costs money; Telegram sufficient; add later if needed |
| **Who manages recipients?** | **Admins only** | Prevent unauthorized access; maintain control |
| **Can viewers self-subscribe?** | ✅ **YES** (via Telegram bot) | Reduces admin workload; users opt-in |
| **How many recipients?** | **Start with 5-10** | Scale to 100+ if needed; architecture supports it |
| **Alert cooldown needed?** | ✅ **YES** (5 minutes) | Prevent spam; avoid notification fatigue |
| **Store alert history?** | ✅ **YES** (30 days) | Compliance, debugging, analytics |

---

## 12. Risk Analysis & Mitigation

### 12.1 Risks
1. **Telegram bot downtime** → Use email as fallback
2. **Alert spam** → Implement cooldown + daily cap
3. **False positives** → Tune thresholds based on data
4. **Recipient overload** → Limit to 50 recipients initially
5. **API rate limits** → Cache data, batch alerts

### 12.2 Success Metrics
- ✅ **Alert Delivery Rate:** > 99.5%
- ✅ **Average Latency:** < 3 seconds (detection → delivery)
- ✅ **User Satisfaction:** > 4.5/5 stars
- ✅ **System Uptime:** > 99.9%
- ✅ **False Positive Rate:** < 2%

---

## 13. Recommended Telegram Bot Setup

### 13.1 Create Bot (5 minutes)
```
1. Open Telegram, search for @BotFather
2. Send: /newbot
3. Choose name: "EvaraTDS Alert Bot"
4. Choose username: "evara_tds_bot" (must end in _bot)
5. Save the bot token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)
6. Send: /setdescription → "Get real-time TDS alerts from EvaraTech"
7. Send: /setabouttext → "Official alert bot for EvaraTDS monitoring"
8. Send: /setcommands → Paste:
   start - Subscribe to alerts
   stop - Unsubscribe from alerts
   status - Check current TDS
   history - View recent alerts
```

### 13.2 Bot Interaction Flow
```
User Action:          Bot Response:
───────────────────────────────────────────────────────────
User sends /start  →  "Welcome to EvaraTDS! You will now 
                       receive alerts when TDS exceeds 
                       150 PPM. Your Chat ID: 123456789"

TDS breach detected → "🚨 CRITICAL ALERT: TDS is 187 PPM 
                       (threshold: 150 PPM). Check dashboard."

User sends /status  → "Current TDS: 142 PPM ✅ SAFE
                       Last updated: 2 seconds ago"

User sends /stop    → "You have unsubscribed from alerts.
                       Send /start to re-subscribe."
```

---

## 14. Deployment Checklist

### 14.1 Backend
- [ ] Set `TELEGRAM_BOT_TOKEN` in environment variables
- [ ] Set `ALERT_EMAIL_FROM` in environment variables
- [ ] Initialize SQLite database with tables
- [ ] Deploy to Railway/Render with persistent storage
- [ ] Test all API endpoints with Postman

### 14.2 Frontend
- [ ] Add Alerts page to navigation (Admin only)
- [ ] Update Settings page with alert configuration
- [ ] Add alert banner component to dashboard
- [ ] Deploy to Vercel
- [ ] Update environment variables

### 14.3 Telegram Bot
- [ ] Start bot server (webhook or long polling)
- [ ] Test /start command from personal Telegram
- [ ] Verify Chat ID is stored in database
- [ ] Send test alert manually

### 14.4 Testing
- [ ] Trigger real TDS breach (or simulate with mock data)
- [ ] Verify alert received on Telegram within 3 seconds
- [ ] Test cooldown (send multiple alerts, verify only 1 per 5 min)
- [ ] Test multiple recipients (add 3-5 test users)
- [ ] Test email fallback (disable Telegram, verify email sent)

---

## 15. Final Recommendation

### ✅ **YES, Implement This Feature**

**Why:**
1. **Industry Standard**: All IoT monitoring systems have alerts
2. **Proactive Monitoring**: Detect issues before they escalate
3. **Cost-Effective**: $0/month with Telegram
4. **Easy to Build**: 6-8 hours total development time
5. **High ROI**: Prevents equipment damage, improves response time

### 🎯 **Recommended Approach:**
- **Phase 1 (MVP):** Telegram bot only, admin recipients, 1-2 hours
- **Phase 2 (Beta):** Add UI, multiple recipients, 2-3 hours
- **Phase 3 (Production):** Email backup, history, analytics, 2-3 hours

### 📋 **Next Steps:**
1. **Approve this architecture** (you're reading it!)
2. **Create Telegram bot** (5 minutes)
3. **Start Phase 1 development** (backend + bot integration)
4. **Deploy MVP** (test with 1-2 users)
5. **Iterate based on feedback**

---

## Questions for Stakeholder Decision:

1. **Who should receive alerts initially?**
   - Recommendation: Start with 1-2 admins (you + 1 other)

2. **What alert channels do you want?**
   - Recommendation: Telegram (free, instant)
   - Optional: Email backup

3. **Do you want SMS alerts?**
   - Recommendation: Skip for now (costs money), add later if needed

4. **Should viewers be able to self-subscribe?**
   - Recommendation: Yes (via Telegram /start command)

5. **What's your budget for alerts?**
   - Recommendation: $0/month (Telegram only) or $5-10/month (with SMS)

---

**Ready to proceed with implementation?** ✅
