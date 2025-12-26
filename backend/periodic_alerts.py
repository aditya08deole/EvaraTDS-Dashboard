"""
Periodic TDS Alert System
Sends water quality status every 15 minutes to Telegram group
Reliable and accurate monitoring
"""
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

from app.services.telegram_service import get_telegram_service
from app.services.thingspeak import ThingSpeakService

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_ALERT_CHAT_ID", "1362954575")
TDS_THRESHOLD = float(os.getenv("TDS_ALERT_THRESHOLD", "150"))
TEMP_THRESHOLD = float(os.getenv("TEMP_ALERT_THRESHOLD", "35"))

async def send_periodic_alert():
    """Send water quality status to Telegram group"""
    try:
        telegram_service = get_telegram_service()
        thingspeak = ThingSpeakService()
        
        # Get latest sensor data
        data = await thingspeak.get_latest_data()
        
        if not data:
            print("⚠️  No sensor data available - will retry in 15 minutes")
            # Send error notification
            await telegram_service.send_alert(
                TELEGRAM_CHAT_ID,
                "⚠️ <b>Sensor Offline</b>\n\nNo data received from ThingSpeak.\nWill check again in 15 minutes."
            )
            return
        
        tds_value = data.get('tds', 0)
        temp_value = data.get('temperature', 0)
        voltage = data.get('voltage', 0)
        timestamp = data.get('created_at', 'Unknown')
        
        # Determine status
        tds_safe = tds_value < TDS_THRESHOLD
        temp_safe = temp_value < TEMP_THRESHOLD
        overall_safe = tds_safe and temp_safe
        
        # Build message
        if overall_safe:
            status_icon = "✅"
            status_text = "SAFE"
            header_emoji = "🌊"
        else:
            status_icon = "⚠️"
            status_text = "ALERT"
            header_emoji = "🚨"
        
        message = f"""{header_emoji} <b>Water Quality Report - {status_text}</b>

{status_icon} <b>Current Readings:</b>
━━━━━━━━━━━━━━━━━━━━
💧 <b>TDS Level: {tds_value:.1f} ppm</b> {'✅' if tds_safe else '⚠️ HIGH'}
   Threshold: {TDS_THRESHOLD} ppm
   Status: {'Safe' if tds_safe else 'Exceeds safe limit'}

🌡️ <b>Temperature: {temp_value:.1f}°C</b> {'✅' if temp_safe else '⚠️ HIGH'}
   Threshold: {TEMP_THRESHOLD}°C
   Status: {'Normal' if temp_safe else 'Above normal'}

⚡ Voltage: {voltage:.2f}V
━━━━━━━━━━━━━━━━━━━━

📊 <b>Overall Status:</b> {'✅ Safe to Use' if overall_safe else '⚠️ Review Required'}

<i>Reading Time: {timestamp}</i>
<i>Report Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</i>
<i>Next update in 15 minutes</i>"""
        
        # Send to Telegram
        await telegram_service.send_alert(TELEGRAM_CHAT_ID, message)
        
        print(f"✅ Alert sent: TDS={tds_value:.1f} ppm, Temp={temp_value:.1f}°C, Status={status_text}")
        
    except Exception as e:
        print(f"❌ Error sending periodic alert: {e}")
        try:
            telegram_service = get_telegram_service()
            await telegram_service.send_alert(
                TELEGRAM_CHAT_ID,
                f"❌ <b>Alert System Error</b>\n\n{str(e)}\n\nWill retry in 15 minutes."
            )
        except:
            pass

async def run_periodic_alerts():
    """Run periodic alert loop - every 15 minutes"""
    print("=" * 60)
    print("🚀 Evara TDS Periodic Alert System")
    print("=" * 60)
    print(f"📍 Telegram Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"📊 TDS Threshold: {TDS_THRESHOLD} ppm")
    print(f"🌡️  Temp Threshold: {TEMP_THRESHOLD}°C")
    print(f"⏱️  Interval: Every 15 minutes (900 seconds)")
    print(f"🔗 Group Link: {os.getenv('TELEGRAM_GROUP_INVITE_LINK', 'Not set')}")
    print("=" * 60)
    print()
    
    # Send startup notification
    try:
        telegram_service = get_telegram_service()
        await telegram_service.send_alert(
            TELEGRAM_CHAT_ID,
            f"""🚀 <b>Alert System Started</b>

Periodic monitoring is now active.
Reports will be sent every 15 minutes.

TDS Threshold: {TDS_THRESHOLD} ppm
Temp Threshold: {TEMP_THRESHOLD}°C

<i>Started at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</i>"""
        )
        print("✅ Startup notification sent")
    except Exception as e:
        print(f"⚠️  Could not send startup notification: {e}")
    
    print()
    print("Starting alert loop...")
    print("-" * 60)
    
    while True:
        await send_periodic_alert()
        print(f"⏳ Waiting 15 minutes until next check...")
        print()
        # Wait 15 minutes (900 seconds)
        await asyncio.sleep(900)

if __name__ == "__main__":
    try:
        asyncio.run(run_periodic_alerts())
    except KeyboardInterrupt:
        print("\n\n⏹️  Alert system stopped by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
