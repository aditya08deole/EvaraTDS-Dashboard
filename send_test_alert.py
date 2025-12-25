import sys
import os
import asyncio
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(env_path)

from app.services.telegram_service import TelegramService

async def main():
    try:
        # Initialize Telegram service
        telegram = TelegramService()
        
        # Get bot info
        print("📤 Connecting to Telegram bot...")
        bot_info = await telegram.get_bot_info()
        print(f"✅ Connected to bot: @{bot_info['username']}")
        
        # Send test alert
        message = """🧪 <b>Test Alert from Evara TDS Platform</b>

This is a test message to confirm your Telegram bot is working!

<b>Bot Details:</b>
• Bot Name: {bot_name}
• Bot Username: @{bot_username}

✅ <b>Congratulations!</b> Your alert system is now configured and working.

You will receive alerts when TDS levels exceed the threshold.""".format(
            bot_name=bot_info.get('first_name', 'EvaraTDS Bot'),
            bot_username=bot_info.get('username', 'EvaraTDS_bot')
        )
        
        chat_id = "1362954575"
        print(f"📤 Sending test alert to chat ID: {chat_id}...")
        
        await telegram.send_alert(chat_id, message)
        
        print("✅ Test alert sent successfully!")
        print(f"\n🎉 Check your Telegram (@EvaraTDS_bot) for the message!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
