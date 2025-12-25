"""
Periodic TDS Alert System
Sends water quality status every 15 minutes to Telegram group
"""
import asyncio
import os
from datetime import datetime
from app.services.telegram_service import get_telegram_service
from app.services.thingspeak import ThingSpeakService
from app.core.config import Settings
import json
from pathlib import Path

settings = Settings()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_ALERT_CHAT_ID", "1362954575")
TDS_THRESHOLD = float(os.getenv("TDS_ALERT_THRESHOLD", "150"))
TEMP_THRESHOLD = float(os.getenv("TEMP_ALERT_THRESHOLD", "35"))

# History file
DATA_DIR = Path("backend/data")
DATA_DIR.mkdir(exist_ok=True, parents=True)
HISTORY_FILE = DATA_DIR / "alert_history.json"

def save_alert_to_history(alert_data: dict):
    """Save alert to history"""
    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except:
            history = []
    
    history.append(alert_data)
    # Keep only last 100
    history = history[-100:]
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2, default=str)

async def send_periodic_alert():
    """Send water quality status to Telegram group"""
    try:
        telegram_service = get_telegram_service()
        thingspeak = ThingSpeakService()
        
        # Get latest sensor data
        data = await thingspeak.get_latest_data()
        
        if not data:
            print("❌ No sensor data available")
            return
        
        tds_value = data.get('tds', 0)
        temp_value = data.get('temperature', 0)
        voltage = data.get('voltage', 0)
        
        # Determine status
        tds_safe = tds_value < TDS_THRESHOLD
        temp_safe = temp_value < TEMP_THRESHOLD
        overall_safe = tds_safe and temp_safe
        
        # Build message
        status_icon = "✅" if overall_safe else "⚠️"
        status_text = "SAFE" if overall_safe else "ALERT"
        
        message = f"""🌊 <b>Water Quality Status - {status_text}</b>

{status_icon} <b>Current Readings:</b>
━━━━━━━━━━━━━━━━━━━━
💧 TDS Level: <b>{tds_value:.1f} ppm</b> {'✅' if tds_safe else '⚠️ HIGH'}
   Threshold: {TDS_THRESHOLD} ppm
   Status: {'Safe' if tds_safe else 'Exceeds safe limit'}

🌡️ Temperature: <b>{temp_value:.1f}°C</b> {'✅' if temp_safe else '⚠️ HIGH'}
   Threshold: {TEMP_THRESHOLD}°C
   Status: {'Normal' if temp_safe else 'Above normal'}

⚡ Voltage: {voltage:.2f}V

━━━━━━━━━━━━━━━━━━━━
📊 <b>Overall Status:</b> {'✅ Safe to Use' if overall_safe else '⚠️ Review Required'}

<i>Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</i>
<i>Next update in 15 minutes</i>"""
        
        # Send to Telegram
        await telegram_service.send_alert(TELEGRAM_CHAT_ID, message)
        
        # Save to history
        alert_data = {
            'id': int(datetime.utcnow().timestamp()),
            'alert_type': 'periodic',
            'severity': 'warning' if not overall_safe else 'info',
            'tds_value': tds_value,
            'temp_value': temp_value,
            'voltage': voltage,
            'tds_safe': tds_safe,
            'temp_safe': temp_safe,
            'overall_safe': overall_safe,
            'message': message,
            'created_at': datetime.utcnow().isoformat(),
            'success': True
        }
        save_alert_to_history(alert_data)
        
        print(f"✅ Periodic alert sent: TDS={tds_value} ppm, Temp={temp_value}°C, Status={status_text}")
        
    except Exception as e:
        print(f"❌ Error sending periodic alert: {e}")
        # Save error to history
        alert_data = {
            'id': int(datetime.utcnow().timestamp()),
            'alert_type': 'periodic',
            'severity': 'error',
            'message': f'Error: {str(e)}',
            'created_at': datetime.utcnow().isoformat(),
            'success': False,
            'error': str(e)
        }
        save_alert_to_history(alert_data)

async def run_periodic_alerts():
    """Run periodic alert loop - every 15 minutes"""
    print(f"🚀 Starting periodic alert system (every 15 minutes)")
    print(f"📍 Sending to Telegram chat ID: {TELEGRAM_CHAT_ID}")
    print(f"📊 TDS Threshold: {TDS_THRESHOLD} ppm")
    print(f"🌡️ Temp Threshold: {TEMP_THRESHOLD}°C")
    print("-" * 50)
    
    while True:
        await send_periodic_alert()
        # Wait 15 minutes (900 seconds)
        await asyncio.sleep(900)

if __name__ == "__main__":
    asyncio.run(run_periodic_alerts())
