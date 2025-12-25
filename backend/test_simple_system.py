"""Quick test of the simplified system"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.telegram_service import get_telegram_service

async def test_system():
    print("🧪 Testing Evara TDS Alert System")
    print("=" * 50)
    
    # Test 1: Bot connection
    print("\n1️⃣ Testing Telegram bot connection...")
    telegram_service = get_telegram_service()
    bot_info = await telegram_service.get_bot_info()
    
    if bot_info:
        print(f"   ✅ Bot connected: @{bot_info.get('username')}")
    else:
        print("   ❌ Bot connection failed!")
        return
    
    # Test 2: Send test message
    print("\n2️⃣ Sending test alert...")
    chat_id = os.getenv("TELEGRAM_ALERT_CHAT_ID", "1362954575")
    group_link = os.getenv("TELEGRAM_GROUP_INVITE_LINK", "https://t.me/+K2URmImZb9tmMDc9")
    
    message = f"""🧪 <b>System Test - Evara TDS Platform</b>

✅ Bot is online and working!
✅ Group invite configured: {group_link}

This is a test message to verify the simplified alert system.

<i>If you see this, everything is working correctly!</i>"""
    
    try:
        await telegram_service.send_alert(chat_id, message)
        print(f"   ✅ Test alert sent to chat ID: {chat_id}")
    except Exception as e:
        print(f"   ❌ Failed to send alert: {e}")
        return
    
    # Test 3: Check data directory
    print("\n3️⃣ Checking JSON storage...")
    from pathlib import Path
    data_dir = Path("backend/data")
    
    if data_dir.exists():
        print(f"   ✅ Data directory exists: {data_dir.absolute()}")
        files = list(data_dir.glob("*.json"))
        if files:
            print(f"   📁 Found {len(files)} JSON file(s):")
            for f in files:
                print(f"      - {f.name}")
        else:
            print("   📝 No JSON files yet (will be created when you add recipients)")
    else:
        print("   ⚠️ Data directory not found (will be created automatically)")
    
    print("\n" + "=" * 50)
    print("✅ System test complete!")
    print("\n📋 Next steps:")
    print("   1. Start backend: python -m uvicorn main:app --reload")
    print("   2. Start periodic alerts: python periodic_alerts.py")
    print("   3. Open dashboard and add recipients")
    print("\n💡 Recipients will automatically get invite link:")
    print(f"   {group_link}")

if __name__ == "__main__":
    asyncio.run(test_system())
