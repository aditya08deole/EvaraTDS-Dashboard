"""
Ultra-Simple Vercel Cron Function - No Complex Dependencies
Sends water quality alerts every 15 minutes
"""
import os
import json
from datetime import datetime
import aiohttp
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8507962260:AAHaRXknIvbEILzEgdK4rJ0rRcMNyV3q2NY")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-4750278606")
THINGSPEAK_CHANNEL_ID = os.getenv("THINGSPEAK_CHANNEL_ID", "2713286")
THINGSPEAK_API_KEY = os.getenv("THINGSPEAK_API_KEY", "EHEK3A1XD48TY98B")

# TDS thresholds
TDS_THRESHOLD = 500
TDS_DANGER = 1000

async def get_thingspeak_data():
    """Fetch latest data from ThingSpeak"""
    url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds/last.json?api_key={THINGSPEAK_API_KEY}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'tds': float(data.get('field1', 0)) if data.get('field1') else 0,
                        'ph': float(data.get('field2', 0)) if data.get('field2') else 0,
                        'turbidity': float(data.get('field3', 0)) if data.get('field3') else 0,
                        'temperature': float(data.get('field4', 0)) if data.get('field4') else 0,
                        'timestamp': data.get('created_at', '')
                    }
    except Exception as e:
        print(f"ThingSpeak error: {e}")
    
    return None

async def send_telegram_message(message: str):
    """Send message to Telegram group"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                return response.status == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def format_alert_message(data):
    """Format beautiful alert message"""
    tds = data['tds']
    ph = data['ph']
    turbidity = data['turbidity']
    temp = data['temperature']
    
    # Determine status
    if tds >= TDS_DANGER:
        status = "🚨 CRITICAL DANGER"
        emoji = "🔴"
    elif tds >= TDS_THRESHOLD:
        status = "⚠️ HIGH ALERT"
        emoji = "🟡"
    else:
        status = "✅ SAFE"
        emoji = "🟢"
    
    message = f"""
╔═══════════════════════════════
║ 💧 *EVARA TDS WATER MONITOR*
╚═══════════════════════════════

🎯 *Status:* {status} {emoji}

📊 *Water Quality Metrics:*
├─ 💎 TDS: *{tds:.2f} ppm*
├─ ⚗️ pH: *{ph:.2f}*
├─ 🌫️ Turbidity: *{turbidity:.2f} NTU*
└─ 🌡️ Temp: *{temp:.2f}°C*

⏰ *Time:* {datetime.now().strftime('%I:%M %p')}
📅 *Date:* {datetime.now().strftime('%b %d, %Y')}

{'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━' if tds < TDS_THRESHOLD else '🚨 ACTION REQUIRED - CHECK WATER IMMEDIATELY!'}
"""
    return message

@app.get("/api/cron/send-alert")
async def send_alert():
    """Main cron endpoint - sends water quality alert"""
    try:
        # Get data from ThingSpeak
        data = await get_thingspeak_data()
        
        if not data:
            return {"status": "error", "message": "Failed to fetch ThingSpeak data"}
        
        # Format and send alert
        message = format_alert_message(data)
        success = await send_telegram_message(message)
        
        if success:
            return {
                "status": "success",
                "message": "Alert sent successfully",
                "tds": data['tds'],
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"status": "error", "message": "Failed to send Telegram message"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/cron/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "bot_token_set": bool(TELEGRAM_BOT_TOKEN),
        "chat_id_set": bool(TELEGRAM_CHAT_ID)
    }

# Vercel serverless handler
handler = Mangum(app)
