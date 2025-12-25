"""
Quick test script to add recipient using serverless storage
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.models.alert import AlertRecipient
from app.services.serverless_storage import ServerlessStorage

def main():
    print("📝 Adding recipient using serverless storage...")
    
    try:
        # Create recipient
        recipient = AlertRecipient(
            name="Aditya",
            telegram_chat_id="1362954575",
            role="admin",
            is_active=True,
            channels=["telegram"],
            created_by="admin"
        )
        
        # Add to storage
        result = ServerlessStorage.add_recipient(recipient)
        print(f"✅ Recipient added successfully!")
        print(f"   ID: {result.id}")
        print(f"   Name: {result.name}")
        print(f"   Chat ID: {result.telegram_chat_id}")
        print(f"   Role: {result.role}")
        
        # List all recipients
        all_recipients = ServerlessStorage.get_recipients(active_only=False)
        print(f"\n📋 Total recipients: {len(all_recipients)}")
        for r in all_recipients:
            print(f"   - {r.name} (ID: {r.id}, Chat: {r.telegram_chat_id})")
        
        print("\n🎉 Setup complete!")
        
    except ValueError as e:
        print(f"⚠️  {e}")
        print("Recipient might already exist.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
