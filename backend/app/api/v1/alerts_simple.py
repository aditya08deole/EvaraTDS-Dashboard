"""
Simple JSON-based alerts system
No database - just JSON storage
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
import os
import json
from pathlib import Path
from datetime import datetime

from app.models.alert import AlertRecipient, AlertHistory, TestAlertRequest
from app.services.telegram_service import get_telegram_service

router = APIRouter()

# JSON storage paths
DATA_DIR = Path("backend/data")
DATA_DIR.mkdir(exist_ok=True, parents=True)
RECIPIENTS_FILE = DATA_DIR / "recipients.json"
HISTORY_FILE = DATA_DIR / "alert_history.json"

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_ALERT_CHAT_ID", "1362954575")
GROUP_INVITE_LINK = os.getenv("TELEGRAM_GROUP_INVITE_LINK", "https://t.me/+K2URmImZb9tmMDc9")

# ===================
# Helper Functions
# ===================

def load_recipients() -> List[dict]:
    """Load recipients from JSON"""
    if not RECIPIENTS_FILE.exists():
        return []
    try:
        with open(RECIPIENTS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_recipients(recipients: List[dict]):
    """Save recipients to JSON"""
    with open(RECIPIENTS_FILE, 'w') as f:
        json.dump(recipients, f, indent=2, default=str)

def load_history() -> List[dict]:
    """Load alert history from JSON"""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_history(history: List[dict]):
    """Save alert history to JSON"""
    # Keep only last 100 alerts
    history = history[-100:]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2, default=str)

# ===================
# Recipients
# ===================

@router.get("/recipients", response_model=List[AlertRecipient])
async def get_recipients(active_only: bool = True):
    """Get all recipients"""
    recipients = load_recipients()
    
    if active_only:
        recipients = [r for r in recipients if r.get('is_active', True)]
    
    return recipients

@router.post("/recipients", response_model=AlertRecipient, status_code=status.HTTP_201_CREATED)
async def create_recipient(recipient: AlertRecipient):
    """Add new recipient and send them group invite"""
    recipients = load_recipients()
    
    # Validate phone number format if provided
    if recipient.phone:
        phone = recipient.phone.strip()
        if not phone.startswith('+'):
            if phone.startswith('91'):
                phone = '+' + phone
            else:
                phone = '+91' + phone
        recipient.phone = phone
        
        # Check for duplicates
        existing = [r for r in recipients if r.get('phone') == phone]
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Phone number already registered"
            )
    
    # Generate ID
    max_id = max([r.get('id', 0) for r in recipients], default=0)
    
    new_recipient = {
        'id': max_id + 1,
        'name': recipient.name,
        'telegram_chat_id': recipient.telegram_chat_id,
        'email': recipient.email,
        'phone': recipient.phone,
        'role': recipient.role,
        'is_active': True,
        'channels': recipient.channels or ["telegram"],
        'created_at': datetime.utcnow().isoformat(),
        'created_by': 'admin'
    }
    
    recipients.append(new_recipient)
    save_recipients(recipients)
    
    # Send group invite if phone provided
    if recipient.phone and GROUP_INVITE_LINK:
        telegram_service = get_telegram_service()
        try:
            message = f"""👋 Hi {recipient.name}!

You've been added to receive water quality alerts from Evara TDS Platform.

🔗 Join our Alert Group: {GROUP_INVITE_LINK}

Once you join, you'll receive real-time alerts about water quality."""
            
            # For now, just log the invite (SMS integration needed for actual sending)
            print(f"📱 Would send invite to {recipient.phone}: {message}")
        except Exception as e:
            print(f"Warning: Could not prepare invite: {e}")
    
    return AlertRecipient(**new_recipient)

@router.delete("/recipients/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipient(recipient_id: int):
    """Delete a recipient"""
    recipients = load_recipients()
    recipients = [r for r in recipients if r.get('id') != recipient_id]
    save_recipients(recipients)
    return None

@router.patch("/recipients/{recipient_id}/toggle", response_model=AlertRecipient)
async def toggle_recipient(recipient_id: int):
    """Activate/deactivate a recipient"""
    recipients = load_recipients()
    
    for i, r in enumerate(recipients):
        if r.get('id') == recipient_id:
            recipients[i]['is_active'] = not r.get('is_active', True)
            save_recipients(recipients)
            return AlertRecipient(**recipients[i])
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")

# ===================
# Alert History
# ===================

@router.get("/history", response_model=List[dict])
async def get_alert_history(limit: int = 50):
    """Get alert history"""
    history = load_history()
    return history[-limit:]

# ===================
# Alert Status
# ===================

@router.get("/status")
async def get_alert_status():
    """Get comprehensive alert system status"""
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
    
    recipients = load_recipients()
    active_recipients = len([r for r in recipients if r.get('is_active', True)])
    
    history = load_history()
    last_alert = history[-1] if history else None
    
    return {
        "telegram_enabled": bot_configured,
        "bot_configured": bot_configured,
        "bot_username": bot_username,
        "active_recipients": active_recipients,
        "total_alerts_sent": len(history),
        "last_alert": last_alert.get('created_at') if last_alert else None,
        "alert_chat_id": TELEGRAM_CHAT_ID,
        "group_invite_link": GROUP_INVITE_LINK
    }

# ===================
# Test Alert
# ===================

@router.post("/test")
async def send_test_alert(request: TestAlertRequest):
    """Send test alert to group"""
    try:
        telegram_service = get_telegram_service()
        bot_info = await telegram_service.get_bot_info()
        
        if not bot_info:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Telegram bot not configured"
            )
        
        recipients_count = len(load_recipients())
        
        message = request.message or f"""🧪 <b>Test Alert from Evara TDS Platform</b>

This is a test message to verify the alert system.

✅ Bot: @{bot_info.get('username', 'Unknown')}
✅ Registered Recipients: {recipients_count}
✅ Alert System: Online

<i>Sent at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</i>"""
        
        try:
            await telegram_service.send_alert(TELEGRAM_CHAT_ID, message)
            success = True
            error_msg = None
        except Exception as e:
            success = False
            error_msg = str(e)
        
        # Log to history
        history = load_history()
        history.append({
            'id': len(history) + 1,
            'alert_type': 'test',
            'severity': 'info',
            'message': request.message or 'Test alert',
            'created_at': datetime.utcnow().isoformat(),
            'success': success,
            'error': error_msg
        })
        save_history(history)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send alert: {error_msg}"
            )
        
        return {
            "success": True,
            "sent_to": "group",
            "chat_id": TELEGRAM_CHAT_ID,
            "registered_recipients": recipients_count,
            "bot_username": bot_info.get('username'),
            "group_invite_link": GROUP_INVITE_LINK
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test alert: {str(e)}"
        )
