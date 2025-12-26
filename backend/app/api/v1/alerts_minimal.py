"""
Ultra-simple alerts API - just status and test
No recipient management - users added manually to Telegram group
"""
from fastapi import APIRouter, HTTPException, status
import os
from datetime import datetime

from app.services.telegram_service import get_telegram_service
from app.services.thingspeak import ThingSpeakService

router = APIRouter()

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_ALERT_CHAT_ID", "1362954575")

@router.get("/status")
async def get_alert_status():
    """Get alert system status"""
    bot_configured = False
    bot_username = None
    
    try:
        telegram_service = get_telegram_service()
        if telegram_service and telegram_service.bot:
            bot_info = await telegram_service.get_bot_info()
            if bot_info:
                bot_configured = True
                bot_username = bot_info.get('username')
    except Exception as e:
        print(f"Bot status check error: {e}")
    
    return {
        "telegram_enabled": bot_configured,
        "bot_configured": bot_configured,
        "bot_username": bot_username,
        "alert_chat_id": TELEGRAM_CHAT_ID,
        "periodic_alerts": "15 minutes",
        "group_link": os.getenv("TELEGRAM_GROUP_INVITE_LINK", "")
    }

@router.post("/test")
async def send_test_alert():
    """Send test alert to verify bot is working"""
    try:
        telegram_service = get_telegram_service()
        bot_info = await telegram_service.get_bot_info()
        
        if not bot_info:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Telegram bot not configured"
            )
        
        # Get current sensor data
        thingspeak = ThingSpeakService()
        data = await thingspeak.get_latest_data()
        
        if data:
            tds = data.get('tds', 0)
            temp = data.get('temperature', 0)
        else:
            tds = 0
            temp = 0
        
        message = f"""🧪 <b>Test Alert - Evara TDS Platform</b>

✅ Bot: @{bot_info.get('username', 'Unknown')}
✅ Alert System: Online

Current Readings:
💧 TDS: {tds:.1f} ppm
🌡️ Temperature: {temp:.1f}°C

<i>Sent at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</i>"""
        
        await telegram_service.send_alert(TELEGRAM_CHAT_ID, message)
        
        return {
            "success": True,
            "chat_id": TELEGRAM_CHAT_ID,
            "bot_username": bot_info.get('username'),
            "tds_value": tds,
            "temp_value": temp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test alert: {str(e)}"
        )
