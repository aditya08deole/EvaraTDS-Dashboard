import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base, DBAlertRecipient, DBAlertConfig

# Database setup
DATABASE_URL = "sqlite:///./backend/alerts.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def main():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if recipient exists
        existing = db.query(DBAlertRecipient).filter(
            DBAlertRecipient.telegram_chat_id == "1362954575"
        ).first()
        
        if existing:
            print(f"✅ Recipient already exists: {existing.name} (ID: {existing.id})")
        else:
            # Add new recipient
            recipient = DBAlertRecipient(
                name="Aditya",
                telegram_chat_id="1362954575",
                role="admin",
                is_active=True,
                channels=["telegram"]
            )
            db.add(recipient)
            db.commit()
            db.refresh(recipient)
            print(f"✅ Recipient added successfully: {recipient.name} (ID: {recipient.id})")
        
        # Check alert config
        config = db.query(DBAlertConfig).first()
        if not config:
            config = DBAlertConfig(
                tds_threshold=150.0,
                temp_threshold=35.0,
                cooldown_minutes=15,
                enabled=True
            )
            db.add(config)
            db.commit()
            print("✅ Alert config initialized")
        else:
            print(f"✅ Alert config exists (Threshold: {config.tds_threshold})")
        
        print("\n🎉 Setup complete!")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
