"""
Vercel Cron Job - Automatic Alerts Every 15 Minutes
This runs on Vercel's infrastructure, no laptop needed!
"""
from fastapi import APIRouter, Request, HTTPException
import os
from datetime import datetime
from app.services.telegram_service import get_telegram_service
from app.services.thingspeak import ThingSpeakService

router = APIRouter()

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_ALERT_CHAT_ID", "1362954575")
TDS_THRESHOLD = float(os.getenv("TDS_ALERT_THRESHOLD", "150"))
TEMP_THRESHOLD = float(os.getenv("TEMP_ALERT_THRESHOLD", "35"))

# Vercel Cron secret for security
CRON_SECRET = os.getenv("CRON_SECRET", "evara-tds-cron-secret-2025")

@router.get("/send-alert")
async def cron_send_alert(request: Request):
    """
    Vercel Cron endpoint - called automatically every 15 minutes
    Secured with secret header
    """
    # Verify cron secret
    auth_header = request.headers.get("authorization")
    if auth_header != f"Bearer {CRON_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        telegram_service = get_telegram_service()
        thingspeak = ThingSpeakService()
        
        # Get latest sensor data
        data = await thingspeak.get_latest_data()
        
        if not data:
            # Send offline notification
            await telegram_service.send_alert(
                TELEGRAM_CHAT_ID,
                "⚠️ <b>Sensor Offline</b>\n\nNo data received from ThingSpeak.\nWill check again in 15 minutes."
            )
            return {"status": "error", "message": "No sensor data"}
        
        tds_value = data.get('tds', 0)
        temp_value = data.get('temperature', 0)
        voltage = data.get('voltage', 0)
        timestamp = data.get('created_at', 'Unknown')
        
        # Determine status
        tds_safe = tds_value < TDS_THRESHOLD
        temp_safe = temp_value < TEMP_THRESHOLD
        overall_safe = tds_safe and temp_safe
        
        # Premium alert message
        if overall_safe:
            status_emoji = "✅"
            status_text = "OPTIMAL"
            header_emoji = "💎"
            status_badge = "🟢"
        else:
            status_emoji = "⚠️"
            status_text = "ALERT"
            header_emoji = "🚨"
            status_badge = "🔴"
        
        message = f"""{header_emoji} <b>EVARA TDS MONITORING REPORT</b> {header_emoji}

{status_badge} <b>Status: {status_text}</b>

━━━━━━━━━━━━━━━━━━━━━━━━
<b>💧 WATER QUALITY METRICS</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>TDS Level</b>
├ Current: <b>{tds_value:.1f} ppm</b> {'✅' if tds_safe else '⚠️'}
├ Threshold: {TDS_THRESHOLD} ppm
└ Status: {'<b>Safe</b>' if tds_safe else '<b>⚠️ High</b>'}

<b>Temperature</b>
├ Current: <b>{temp_value:.1f}°C</b> {'✅' if temp_safe else '⚠️'}
├ Threshold: {TEMP_THRESHOLD}°C
└ Status: {'<b>Normal</b>' if temp_safe else '<b>⚠️ High</b>'}

<b>System</b>
└ Voltage: {voltage:.2f}V

━━━━━━━━━━━━━━━━━━━━━━━━
{status_emoji} <b>Overall Assessment</b>
{'✅ Water quality is <b>SAFE</b> for use' if overall_safe else '⚠️ <b>REVIEW REQUIRED</b> - Parameters exceed safe limits'}

━━━━━━━━━━━━━━━━━━━━━━━━
<i>📊 Reading Time: {timestamp}</i>
<i>🕐 Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</i>
<i>⏰ Next Report: 15 minutes</i>

<i>Powered by Evara TDS Platform 💎</i>"""
        
        # Send to Telegram
        await telegram_service.send_alert(TELEGRAM_CHAT_ID, message)
        
        return {
            "status": "success",
            "tds": tds_value,
            "temperature": temp_value,
            "safe": overall_safe,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Send error notification
        try:
            telegram_service = get_telegram_service()
            await telegram_service.send_alert(
                TELEGRAM_CHAT_ID,
                f"❌ <b>Alert System Error</b>\n\n{str(e)}\n\nWill retry in 15 minutes."
            )
        except:
            pass
        
        return {"status": "error", "message": str(e)}

@router.get("/health")
async def cron_health():
    """Health check for cron job"""
    try:
        telegram_service = get_telegram_service()
        bot_info = await telegram_service.get_bot_info()
        
        return {
            "status": "healthy",
            "bot": bot_info.get('username') if bot_info else None,
            "chat_id": TELEGRAM_CHAT_ID,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
