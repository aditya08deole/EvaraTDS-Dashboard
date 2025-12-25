"""
Standalone script to add recipient and send test alert
Run this while backend server is stopped
"""
import os
import sys
import asyncio

# Set up path
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

from dotenv import load_dotenv
load_dotenv('.env')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import DBAlertRecipient, DBAlertConfig, Base
from app.services.telegram_service import TelegramService

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./alerts.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def main():
    db = SessionLocal()
    
    try:
        # 1. Add recipient
        print("📝 Adding recipient...")
        existing = db.query(DBAlertRecipient).filter(
            DBAlertRecipient.telegram_chat_id == "1362954575"
        ).first()
        
        if existing:
            print(f"✅ Recipient already exists: {existing.name} (ID: {existing.id})")
        else:
            new_recipient = DBAlertRecipient(
                name="Aditya",
                telegram_chat_id="1362954575",
                role="admin",
                is_active=True,
                channels=["telegram"]
            )
            db.add(new_recipient)
            db.commit()
            db.refresh(new_recipient)
            print(f"✅ Recipient added: {new_recipient.name} (ID: {new_recipient.id})")
        
        # 2. Initialize default config if not exists
        config = db.query(DBAlertConfig).first()
        if not config:
            config = DBAlertConfig(
                tds_threshold=150.0,
                temp_threshold=35.0,
                cooldown_minutes=15
            )
            db.add(config)
            db.commit()
            print("✅ Alert config initialized")
        
        # 3. Send test alert
        print("\n📤 Sending test alert...")
        telegram = TelegramService()
        
        bot_info = await telegram.get_bot_info()
        if not bot_info:
            print("❌ Telegram bot not configured. Check TELEGRAM_BOT_TOKEN in .env")
            return
        
        print(f"✅ Bot: @{bot_info['username']}")
        
        test_message = """
🧪 <b>TEST ALERT</b>

This is a test alert from Evara TDS Platform!

If you receive this, your alert system is working perfectly! 🎉

<b>Bot Info:</b>
• Username: @{}
• Name: {}

<i>Setup complete!</i>
""".format(bot_info['username'], bot_info['first_name'])
        
        success = await telegram.send_alert("1362954575", test_message)
        
        if success:
            print("✅ Test alert sent successfully!")
            print("\n🎉 Setup complete! Check your Telegram for the message.")
        else:
            print("❌ Failed to send test alert")
            print("   Make sure you sent /start to the bot first")
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
