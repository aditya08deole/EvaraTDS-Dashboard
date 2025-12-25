"""
Alert API Endpoints - Production-ready serverless storage
Optimized for Vercel deployment with JSON storage
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.alert import AlertRecipient, AlertHistory, AlertConfig, TestAlertRequest
from app.services.serverless_storage import ServerlessStorage
from app.services.telegram_service import get_telegram_service
import asyncio

router = APIRouter(prefix="/alerts", tags=["alerts"])

# =====================
# Recipients Management
# =====================

@router.post("/recipients", response_model=AlertRecipient, status_code=status.HTTP_201_CREATED)
async def create_recipient(recipient: AlertRecipient):
    """Add new alert recipient"""
    try:
        return ServerlessStorage.add_recipient(recipient)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {str(e)}")

@router.get("/recipients", response_model=List[AlertRecipient])
async def get_recipients(active_only: bool = True):
    """Get all recipients"""
    return ServerlessStorage.get_recipients(active_only=active_only)

@router.get("/recipients/{recipient_id}", response_model=AlertRecipient)
async def get_recipient(recipient_id: int):
    """Get specific recipient"""
    recipient = ServerlessStorage.get_recipient_by_id(recipient_id)
    if not recipient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")
    return recipient

@router.delete("/recipients/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipient(recipient_id: int):
    """Delete a recipient"""
    if not ServerlessStorage.delete_recipient(recipient_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")
    return None

@router.patch("/recipients/{recipient_id}/toggle", response_model=AlertRecipient)
async def toggle_recipient(recipient_id: int):
    """Activate/deactivate a recipient"""
    recipient = ServerlessStorage.get_recipient_by_id(recipient_id)
    if not recipient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")
    
    updated = ServerlessStorage.update_recipient(recipient_id, {'is_active': not recipient.is_active})
    if not updated:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update")
    return updated

# ===================
# Alert History
# ===================

@router.get("/history", response_model=List[AlertHistory])
async def get_alert_history(limit: int = 50, alert_type: Optional[str] = None):
    """Get alert history"""
    history = ServerlessStorage.get_alert_history(limit=limit)
    if alert_type:
        history = [h for h in history if h.alert_type == alert_type]
    return history

# ===================
# Configuration
# ===================

@router.get("/config", response_model=AlertConfig)
async def get_config():
    """Get alert configuration"""
    config = ServerlessStorage.get_config()
    if not config:
        # Return default config
        default_config = AlertConfig(
            id=1,
            tds_threshold=150.0,
            warning_threshold=120.0,
            cooldown_minutes=15,
            enable_telegram=True,
            enable_email=False,
            enable_sms=False,
            enabled=True
        )
        ServerlessStorage.update_config(default_config)
        return default_config
    return config

@router.put("/config", response_model=AlertConfig)
async def update_config(config: AlertConfig):
    """Update alert configuration"""
    return ServerlessStorage.update_config(config)

# ===================
# Alert Status
# ===================

@router.get("/status")
async def get_alert_status():
    """Get comprehensive alert system status"""
    try:
        telegram_service = get_telegram_service()
        bot_info = await telegram_service.get_bot_info()
        bot_configured = bot_info is not None
        bot_username = bot_info.get('username') if bot_info else None
    except:
        bot_configured = False
        bot_username = None
    
    recipients = ServerlessStorage.get_recipients(active_only=True)
    config = ServerlessStorage.get_config()
    history = ServerlessStorage.get_alert_history(limit=1)
    
    last_alert_time = None
    if history:
        try:
            last_alert_time = datetime.fromisoformat(history[0].created_at)
        except:
            pass
    
    cooldown_remaining = 0
    can_send_alert = True
    
    if last_alert_time and config:
        time_since_last = datetime.utcnow() - last_alert_time
        cooldown_seconds = config.cooldown_minutes * 60
        if time_since_last.total_seconds() < cooldown_seconds:
            cooldown_remaining = int(cooldown_seconds - time_since_last.total_seconds())
            can_send_alert = False
    
    return {
        "telegram_enabled": bot_configured,
        "tds_threshold": config.tds_threshold if config else 150.0,
        "temp_threshold": config.warning_threshold if config else 35.0,
        "cooldown_minutes": config.cooldown_minutes if config else 15,
        "last_alert": last_alert_time.isoformat() if last_alert_time else None,
        "cooldown_remaining": cooldown_remaining,
        "can_send_alert": can_send_alert,
        "bot_configured": bot_configured,
        "bot_username": bot_username,
        "active_recipients": len(recipients),
        "total_alerts_sent": len(history)
    }

# ===================
# Test Alert
# ===================

@router.post("/test")
async def send_test_alert(request: TestAlertRequest):
    """Send test alert to all active recipients"""
    try:
        telegram_service = get_telegram_service()
        bot_info = await telegram_service.get_bot_info()
        
        if not bot_info:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Telegram bot not configured"
            )
        
        recipients = ServerlessStorage.get_recipients(active_only=True)
        if not recipients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active recipients configured"
            )
        
        success_count = 0
        errors = []
        
        message = request.message or f"""🧪 <b>Test Alert</b>

This is a test message from Evara TDS Platform.

✅ Bot: @{bot_info.get('username', 'Unknown')}
✅ Recipients: {len(recipients)}
✅ Alerts System: Online

<i>Sent at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</i>"""
        
        for recipient in recipients:
            if recipient.telegram_chat_id and 'telegram' in recipient.channels:
                try:
                    await telegram_service.send_alert(recipient.telegram_chat_id, message)
                    success_count += 1
                except Exception as e:
                    errors.append(f"{recipient.name}: {str(e)}")
        
        # Log to history
        alert_history = AlertHistory(
            alert_type="test",
            severity="info",
            message=request.message or "Test alert",
            recipients_notified=[r.telegram_chat_id for r in recipients if r.telegram_chat_id],
            channels_used=["telegram"],
            delivery_status={"success": success_count, "failed": len(errors)},
            recipient_count=len(recipients)
        )
        ServerlessStorage.add_alert_history(alert_history)
        
        return {
            "success": True,
            "recipients_total": len(recipients),
            "sent_successfully": success_count,
            "failed": len(errors),
            "errors": errors if errors else None,
            "bot_username": bot_info.get('username')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test alert: {str(e)}"
        )

# ===================
# Telegram Webhook
# ===================

@router.post("/webhook")
async def telegram_webhook(update: dict):
    """Handle Telegram webhook updates (for bot commands like /start)"""
    try:
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        
        if text == "/start" and chat_id:
            telegram_service = get_telegram_service()
            
            # Check if already registered
            recipients = ServerlessStorage.get_recipients(active_only=False)
            existing = any(r.telegram_chat_id == str(chat_id) for r in recipients)
            
            if not existing:
                # Auto-register user
                user = message.get("from", {})
                first_name = user.get("first_name", "User")
                username = user.get("username", "")
                
                new_recipient = AlertRecipient(
                    name=f"{first_name} (@{username})" if username else first_name,
                    telegram_chat_id=str(chat_id),
                    role="viewer",
                    is_active=True,
                    channels=["telegram"],
                    created_by="telegram_webhook"
                )
                
                ServerlessStorage.add_recipient(new_recipient)
                
                welcome_msg = f"""👋 Welcome to Evara TDS Alert System!

You've been registered to receive water quality alerts.

<b>Your Details:</b>
• Chat ID: {chat_id}
• Status: Active

You'll receive notifications when:
• TDS levels exceed safe thresholds
• Temperature anomalies detected
• System updates available

Use /help for more commands."""
            else:
                welcome_msg = f"""✅ You're already registered!

Chat ID: {chat_id}
Status: Active

You're receiving water quality alerts."""
            
            await telegram_service.send_alert(str(chat_id), welcome_msg)
        
        return {"ok": True}
        
    except Exception as e:
        return {"ok": False, "error": str(e)}
