# 🌊 Evara TDS Monitoring Platform

> **Professional IoT dashboard for real-time Total Dissolved Solids (TDS) monitoring with intelligent alerts**

[![Status](https://img.shields.io/badge/status-production--ready-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![Python](https://img.shields.io/badge/python-3.12-blue)]()
[![React](https://img.shields.io/badge/react-18.2-blue)]()

---

## 🎯 Overview

**Evara TDS Platform** is an enterprise-grade monitoring solution that provides real-time water quality analytics with automatic threshold alerts via Telegram. Built with modern web technologies for scalability and reliability.

### Key Features

✨ **Real-Time Monitoring** - 1-second sensor data updates  
🔔 **Smart Alerts** - Telegram notifications with cooldown logic  
📊 **Historical Analytics** - Data logging with CSV export  
🎨 **Glassmorphic UI** - Professional dark theme interface  
🔐 **Role-Based Access** - Admin and Viewer authentication  
⚡ **Ultra-Fast** - Optimized for minimal latency  
🗃️ **SQLite Database** - Alert history and recipient management  

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 18+**
- **Telegram Account** (for alerts)

### Installation

```bash
# Clone repository
git clone https://github.com/aditya08deole/EvaraTDS-Dashboard.git
cd evara-tds-platform

# Backend setup
cd backend
pip install -r requirement.txt

# Frontend setup
cd ../frontend
npm install
```

### Configuration

1. **Create Telegram Bot**
   ```bash
   # Open Telegram → Search @BotFather → Send /newbot
   # Copy token and add to backend/.env
   ```

2. **Backend Environment** (`backend/.env`)
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TDS_ALERT_THRESHOLD=150.0
   ALERT_COOLDOWN_MINUTES=15
   ```

3. **Frontend Environment** (`frontend/.env`)
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

### Run Application

```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Access:** http://localhost:5173

**Login Credentials:**
- Admin: `Aditya.Evaratech` / `[password in .env]`
- Viewer: `user` / `pass@123`

---

## 📖 Documentation

- 📘 **[Alert Setup Guide](ALERT_SETUP_GUIDE.md)** - Complete alert system configuration
- 🏗️ **[System Architecture](ALERT_SYSTEM_ARCHITECTURE.md)** - Technical deep-dive
- 🚀 **[Deployment Guide](DEPLOYMENT.md)** - Production deployment steps
- ⚙️ **[Vercel Setup](VERCEL_ENV_SETUP.md)** - Environment configuration

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌────────────┐
│   Frontend  │─────▶│   Backend    │─────▶│ ThingSpeak │
│  React/TS   │ HTTP │ FastAPI/Py   │ REST │   IoT API  │
└─────────────┘      └──────────────┘      └────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ Alert Engine │
                     │  + Telegram  │
                     └──────────────┘
```

### Tech Stack

**Frontend:**
- React 18.2 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- Zustand (state management)
- Recharts (data visualization)

**Backend:**
- FastAPI (REST API)
- SQLAlchemy (ORM)
- python-telegram-bot (alerts)
- Uvicorn (ASGI server)
- SQLite (database)

**IoT Integration:**
- ThingSpeak API (sensor data)
- Real-time polling (1-second intervals)

---

## 🔔 Alert System

### How It Works

1. **Threshold Monitoring** - Continuously checks TDS/temperature values
2. **Smart Cooldown** - Prevents spam (15-minute default)
3. **Multi-Recipient** - Supports multiple Telegram users
4. **Delivery Tracking** - Logs all alerts in database
5. **Test Mode** - Verify setup before going live

### Setup Alerts

1. Navigate to `/alerts` page
2. Click "Add Recipient"
3. Enter Telegram chat ID (get from `/start` → getUpdates)
4. Click "Send Test Alert" to verify
5. Configure thresholds via "Configure" button

**See:** [ALERT_SETUP_GUIDE.md](ALERT_SETUP_GUIDE.md) for detailed instructions

---

## 📊 API Endpoints

### Sensor Data
- `GET /api/v1/sensor/latest` - Latest readings
- `GET /api/v1/sensor/history` - Historical data

### Alerts
- `POST /api/v1/alerts/recipients` - Add recipient
- `GET /api/v1/alerts/recipients` - List recipients
- `POST /api/v1/alerts/test` - Send test alert
- `GET /api/v1/alerts/status` - System status
- `GET /api/v1/alerts/history` - Alert history
- `PUT /api/v1/alerts/config` - Update thresholds

### Health
- `GET /health` - Server health check

**Full API Docs:** http://localhost:8000/docs (when backend running)

---

## 🔐 Security

✅ **Environment Variables** - All secrets in `.env` (never committed)  
✅ **Token Validation** - Format checks without exposure  
✅ **Rate Limiting** - 200 requests/minute per IP  
✅ **CORS Protection** - Whitelist-based origins  
✅ **Session Management** - Secure client-side auth  

**Important:** Never commit `.env` files (already in `.gitignore`)

---

## 🧪 Testing

### Manual Testing

```bash
# Test alert system
curl -X POST http://localhost:8000/api/v1/alerts/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Test alert"}'

# Check sensor data
curl http://localhost:8000/api/v1/sensor/latest

# System status
curl http://localhost:8000/api/v1/alerts/status
```

### Test Threshold Trigger

1. Go to Alerts → Configure
2. Set TDS threshold to `50` (very low)
3. Save and wait for next reading
4. You'll receive an alert!
5. **Reset threshold to 150** after testing

---

## 📁 Project Structure

```
evara-tds-platform/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── requirement.txt         # Python dependencies
│   ├── .env                    # Environment variables (local)
│   ├── app/
│   │   ├── api/v1/            # API endpoints
│   │   │   ├── alerts.py      # Alert management
│   │   │   └── endpoints.py   # Sensor endpoints
│   │   ├── models/            # Database models
│   │   │   ├── database.py    # SQLAlchemy setup
│   │   │   └── alert.py       # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   │   ├── alert_engine.py     # Threshold monitoring
│   │   │   ├── telegram_service.py # Bot integration
│   │   │   └── thingspeak.py      # IoT API client
│   │   └── core/              # Configuration
│   │       └── config.py
│   └── scripts/
│       └── verify_bot.py      # Bot verification tool
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── src/
│       ├── main.tsx           # React entry point
│       ├── App.tsx            # Router + routes
│       ├── pages/             # Page components
│       │   ├── Login.tsx      # Authentication
│       │   ├── Alerts.tsx     # Alert management
│       │   ├── History.tsx    # Data logs
│       │   └── Settings.tsx   # Calibration
│       ├── components/        # Reusable components
│       │   ├── Dashboard.tsx  # Main monitoring view
│       │   ├── StatCard.tsx   # Metric cards
│       │   └── layout/
│       │       └── GlassLayout.tsx
│       ├── store/             # Zustand state
│       │   ├── useAuthStore.ts
│       │   ├── useSensorStore.ts
│       │   └── useSettingsStore.ts
│       └── services/
│           └── AuthService.ts
│
├── ALERT_SETUP_GUIDE.md       # Alert configuration guide
├── ALERT_SYSTEM_ARCHITECTURE.md # Technical architecture
├── DEPLOYMENT.md              # Production deployment
├── VERCEL_ENV_SETUP.md        # Vercel configuration
└── README.md                  # This file
```

---

## 🚀 Deployment

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

### Backend (Railway)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**See:** [DEPLOYMENT.md](DEPLOYMENT.md) for detailed steps

---

## 🐛 Troubleshooting

### Common Issues

**"Telegram bot not configured"**
- Verify `TELEGRAM_BOT_TOKEN` in `backend/.env`
- Restart backend after changing `.env`

**"No active recipients"**
- Add recipients via `/alerts` page
- Ensure chat ID is correct (numeric)

**Alerts not sending**
- Check you sent `/start` to bot
- Verify bot token is correct
- Check alert history for errors

**Frontend not connecting**
- Verify backend is running on port 8000
- Check CORS settings in `backend/main.py`

**See:** [ALERT_SETUP_GUIDE.md](ALERT_SETUP_GUIDE.md) for more troubleshooting

---

## 📈 Roadmap

### Phase 2 (Planned)
- 📧 Email alerts (Resend API)
- 📞 SMS alerts (Twilio)
- 📊 Advanced analytics dashboard
- 🔗 Webhook integrations (Slack, Discord)

### Phase 3 (Future)
- 📅 Scheduled reports
- 🎨 Custom alert templates
- 🤖 Machine learning predictions
- 📱 Mobile app (React Native)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Aditya Deole**  
*Evara Technologies*

- GitHub: [@aditya08deole](https://github.com/aditya08deole)
- Repository: [EvaraTDS-Dashboard](https://github.com/aditya08deole/EvaraTDS-Dashboard)

---

## 🙏 Acknowledgments

- ThingSpeak IoT Platform
- Telegram Bot API
- FastAPI Framework
- React Community

---

## 📞 Support

For issues or questions:
1. Check [ALERT_SETUP_GUIDE.md](ALERT_SETUP_GUIDE.md)
2. Review [API Documentation](http://localhost:8000/docs)
3. Open GitHub Issue

---

**Built with ❤️ by Evara Technologies**
