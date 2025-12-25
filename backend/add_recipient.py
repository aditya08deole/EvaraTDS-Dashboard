"""
Quick script to add recipient directly to database
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv('.env')

from app.models.database import SessionLocal, DBAlertRecipient, init_db

# Initialize database
init_db()

# Create session
db = SessionLocal()

try:
    # Check if recipient already exists
    existing = db.query(DBAlertRecipient).filter(
        DBAlertRecipient.telegram_chat_id == "1362954575"
    ).first()
    
    if existing:
        print(f"✅ Recipient already exists: {existing.name} (ID: {existing.id})")
        print(f"   Chat ID: {existing.telegram_chat_id}")
        print(f"   Active: {existing.is_active}")
    else:
        # Add new recipient
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
        
        print(f"✅ Recipient added successfully!")
        print(f"   Name: {new_recipient.name}")
        print(f"   Chat ID: {new_recipient.telegram_chat_id}")
        print(f"   Role: {new_recipient.role}")
        print(f"   ID: {new_recipient.id}")

finally:
    db.close()
