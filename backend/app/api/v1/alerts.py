"""
Alert API Endpoints - Simplified Telegram Group version
Sends alerts directly to configured Telegram group/chat
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import os
from app.models.alert import AlertRecipient, AlertHistory, AlertConfig, TestAlertRequest
from app.models.postgres_db import (
    get_db, 
    init_db,
    DBAlertRecipient,
    DBAlertHistory,
    DBAlertConfig
)
from app.services.telegram_service import get_telegram_service
import asyncio

router = APIRouter(prefix="/alerts", tags=["alerts"])

# Initialize database on module load
init_db()

# Get configured Telegram chat ID from environment
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_ALERT_CHAT_ID", "1362954575")

# =====================
# Recipients Management
# =====================

@router.post("/recipients", response_model=AlertRecipient, status_code=status.HTTP_201_CREATED)
async def create_recipient(recipient: AlertRecipient, db: Session = Depends(get_db)):
    """
    Add new alert recipient and send them group invite
    Now supports phone numbers - will send invite via Telegram/SMS
    """
    try:
        # Validate phone number format if provided
        if recipient.phone:
            # Ensure it starts with country code
            phone = recipient.phone.strip()
            if not phone.startswith('+'):
                if phone.startswith('91'):  # India
                    phone = '+' + phone
                else:
                    phone = '+91' + phone  # Default to India
            recipient.phone = phone
        
        # Check for duplicates
        if recipient.phone:
            existing = db.query(DBAlertRecipient).filter(
                DBAlertRecipient.phone == recipient.phone
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Phone number already registered for {existing.name}"
                )
        
        db_recipient = DBAlertRecipient(
            name=recipient.name,
            telegram_chat_id=recipient.telegram_chat_id,
            email=recipient.email,
            phone=recipient.phone,
            role=recipient.role,
            is_active=recipient.is_active if recipient.is_active is not None else True,
            channels=recipient.channels or ["telegram"],
            created_by=recipient.created_by or "api"
        )
        db.add(db_recipient)
        db.commit()
        db.refresh(db_recipient)
        
        # Send group invite if phone number provided
        if recipient.phone:
            telegram_service = get_telegram_service()
            group_invite_link = os.getenv("TELEGRAM_GROUP_INVITE_LINK", "")
            
            if group_invite_link:
                try:
                    await telegram_service.send_invite_via_phone(
                        recipient.phone,
                        recipient.name,
                        group_invite_link
                    )
                except Exception as e:
                    # Don't fail the whole request if invite fails
                    print(f"Warning: Could not send invite to {recipient.phone}: {e}")
        
        return AlertRecipient(
            id=db_recipient.id,
            name=db_recipient.name,
            telegram_chat_id=db_recipient.telegram_chat_id,
            email=db_recipient.email,
            phone=db_recipient.phone,
            role=db_recipient.role,
            is_active=db_recipient.is_active,
            channels=db_recipient.channels,
            created_at=db_recipient.created_at,
            created_by=db_recipient.created_by
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recipient: {str(e)}"
        )

@router.get("/recipients", response_model=List[AlertRecipient])
async def get_recipients(active_only: bool = True, db: Session = Depends(get_db)):
    """Get all recipients"""
    query = db.query(DBAlertRecipient)
    if active_only:
        query = query.filter(DBAlertRecipient.is_active == True)
    
    recipients = query.all()
    return [
        AlertRecipient(
            id=r.id,
            name=r.name,
            telegram_chat_id=r.telegram_chat_id,
            email=r.email,
            phone=r.phone,
            role=r.role,
            is_active=r.is_active,
            channels=r.channels or ["telegram"],
            created_at=r.created_at,
            created_by=r.created_by
        )
        for r in recipients
    ]

@router.get("/recipients/{recipient_id}", response_model=AlertRecipient)
async def get_recipient(recipient_id: int, db: Session = Depends(get_db)):
    """Get specific recipient"""
    recipient = db.query(DBAlertRecipient).filter(DBAlertRecipient.id == recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")
    
    return AlertRecipient(
        id=recipient.id,
        name=recipient.name,
        telegram_chat_id=recipient.telegram_chat_id,
        email=recipient.email,
        phone=recipient.phone,
        role=recipient.role,
        is_active=recipient.is_active,
        channels=recipient.channels or ["telegram"],
        created_at=recipient.created_at,
        created_by=recipient.created_by
    )

@router.delete("/recipients/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipient(recipient_id: int, db: Session = Depends(get_db)):
    """Delete a recipient"""
    recipient = db.query(DBAlertRecipient).filter(DBAlertRecipient.id == recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")
    
    db.delete(recipient)
    db.commit()
    return None

@router.patch("/recipients/{recipient_id}/toggle", response_model=AlertRecipient)
async def toggle_recipient(recipient_id: int, db: Session = Depends(get_db)):
    """Activate/deactivate a recipient"""
    recipient = db.query(DBAlertRecipient).filter(DBAlertRecipient.id == recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")
    
    recipient.is_active = not recipient.is_active
    db.commit()
    db.refresh(recipient)
    
    return AlertRecipient(
        id=recipient.id,
        name=recipient.name,
        telegram_chat_id=recipient.telegram_chat_id,
        email=recipient.email,
        phone=recipient.phone,
        role=recipient.role,
        is_active=recipient.is_active,
        channels=recipient.channels or ["telegram"],
        created_at=recipient.created_at,
        created_by=recipient.created_by
    )

# ===================
# Alert History
# ===================

@router.get("/history", response_model=List[AlertHistory])
async def get_alert_history(
    limit: int = 50,
    alert_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get alert history"""
    query = db.query(DBAlertHistory).order_by(DBAlertHistory.created_at.desc())
    if alert_type:
        query = query.filter(DBAlertHistory.alert_type == alert_type)
    
    history = query.limit(limit).all()
    return [
        AlertHistory(
            id=h.id,
            alert_type=h.alert_type,
            severity=h.severity,
            message=h.message,
            tds_value=h.tds_value,
            temp_value=h.temp_value,
            voltage_value=h.voltage_value,
            threshold=h.threshold,
            recipients_notified=h.recipients_notified or [],
            channels_used=h.channels_used or [],
            delivery_status=h.delivery_status or {},
            recipient_count=h.recipient_count,
            created_at=h.created_at
        )
        for h in history
    ]

# ===================
# Configuration
# ===================

@router.get("/config", response_model=AlertConfig)
async def get_config(db: Session = Depends(get_db)):
    """Get alert configuration"""
    config = db.query(DBAlertConfig).first()
    if not config:
        # Create default
        config = DBAlertConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    
    return AlertConfig(
        id=config.id,
        tds_threshold=config.tds_threshold,
        warning_threshold=config.warning_threshold,
        cooldown_minutes=config.cooldown_minutes,
        enable_telegram=config.enable_telegram,
        enable_email=config.enable_email,
        enable_sms=config.enable_sms,
        enabled=config.enabled
    )

@router.put("/config", response_model=AlertConfig)
async def update_config(config_update: AlertConfig, db: Session = Depends(get_db)):
    """Update alert configuration"""
    config = db.query(DBAlertConfig).first()
    if not config:
        config = DBAlertConfig()
        db.add(config)
    
    config.tds_threshold = config_update.tds_threshold
    config.warning_threshold = config_update.warning_threshold
    config.cooldown_minutes = config_update.cooldown_minutes
    config.enable_telegram = config_update.enable_telegram
    config.enable_email = config_update.enable_email
    config.enable_sms = config_update.enable_sms
    config.enabled = config_update.enabled
    
    db.commit()
    db.refresh(config)
    
    return AlertConfig(
        id=config.id,
        tds_threshold=config.tds_threshold,
        warning_threshold=config.warning_threshold,
        cooldown_minutes=config.cooldown_minutes,
        enable_telegram=config.enable_telegram,
        enable_email=config.enable_email,
        enable_sms=config.enable_sms,
        enabled=config.enabled
    )

# ===================
# Alert Status
# ===================

@router.get("/status")
async def get_alert_status(db: Session = Depends(get_db)):
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
    
    config = db.query(DBAlertConfig).first()
    history = db.query(DBAlertHistory).order_by(DBAlertHistory.created_at.desc()).first()
    
    last_alert_time = history.created_at if history else None
    cooldown_remaining = 0
    can_send_alert = True
    
    if last_alert_time and config:
        time_since_last = datetime.utcnow() - last_alert_time
        cooldown_seconds = config.cooldown_minutes * 60
        if time_since_last.total_seconds() < cooldown_seconds:
            cooldown_remaining = int(cooldown_seconds - time_since_last.total_seconds())
            can_send_alert = False
    
    total_alerts = db.query(DBAlertHistory).count()
    
    return {
        "telegram_enabled": bot_configured,
        "tds_threshold": config.tds_threshold if config else 150.0,
        "temp_threshold": config.temp_threshold if config else 35.0,
        "cooldown_minutes": config.cooldown_minutes if config else 15,
        "last_alert": last_alert_time.isoformat() if last_alert_time else None,
        "cooldown_remaining": cooldown_remaining,
        "can_send_alert": can_send_alert,
        "bot_configured": bot_configured,
        "bot_username": bot_username,
        "active_recipients": 1 if bot_configured else 0,  # Simplified: using group chat
        "total_alerts_sent": total_alerts,
        "alert_chat_id": TELEGRAM_CHAT_ID
    }

# ===================
# Test Alert
# ===================

@router.post("/test")
async def send_test_alert(request: TestAlertRequest, db: Session = Depends(get_db)):
    """Send test alert to the Telegram group"""
    try:
        telegram_service = get_telegram_service()
        bot_info = await telegram_service.get_bot_info()
        
        if not bot_info:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Telegram bot not configured"
            )
        
        # Use group chat ID from environment
        group_chat_id = os.getenv("TELEGRAM_GROUP_CHAT_ID", TELEGRAM_CHAT_ID)
        recipients_count = db.query(DBAlertRecipient).filter(DBAlertRecipient.is_active == True).count()
        
        message = request.message or f"""🧪 <b>Test Alert from Evara TDS Platform</b>

This is a test message to verify the alert system is working.

✅ Bot: @{bot_info.get('username', 'Unknown')}
✅ Registered Recipients: {recipients_count}
✅ Alert System: Online

<i>Sent at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</i>"""
        
        try:
            await telegram_service.send_group_alert(group_chat_id, message)
            success = True
            error_msg = None
        except Exception as e:
            success = False
            error_msg = str(e)
        
        # Log to history
        alert_history = DBAlertHistory(
            alert_type="test",
            severity="info",
            message=request.message or "Test alert",
            recipients_notified=[group_chat_id] if success else [],
            channels_used=["telegram"],
            delivery_status={"success": 1 if success else 0, "failed": 0 if success else 1, "error": error_msg},
            recipient_count=recipients_count
        )
        db.add(alert_history)
        db.commit()
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send to group: {error_msg}"
            )
        
        return {
            "success": True,
            "sent_to": "group",
            "group_chat_id": group_chat_id,
            "registered_recipients": recipients_count,
            "bot_username": bot_info.get('username')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test alert: {str(e)}"
        )

# ===================
# Telegram Webhook
# ===================

@router.post("/webhook")
async def telegram_webhook(update: dict, db: Session = Depends(get_db)):
    """Handle Telegram webhook updates"""
    try:
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        
        if text == "/start" and chat_id:
            telegram_service = get_telegram_service()
            
            # Check if already registered
            existing = db.query(DBAlertRecipient).filter(
                DBAlertRecipient.telegram_chat_id == str(chat_id)
            ).first()
            
            if not existing:
                # Auto-register user
                user = message.get("from", {})
                first_name = user.get("first_name", "User")
                username = user.get("username", "")
                
                new_recipient = DBAlertRecipient(
                    name=f"{first_name} (@{username})" if username else first_name,
                    telegram_chat_id=str(chat_id),
                    role="viewer",
                    is_active=True,
                    channels=["telegram"],
                    created_by="telegram_webhook"
                )
                
                db.add(new_recipient)
                db.commit()
                
                welcome_msg = f"""👋 Welcome to Evara TDS Alert System!

You've been registered to receive water quality alerts.

<b>Your Details:</b>
• Chat ID: {chat_id}
• Status: Active

You'll receive notifications when TDS levels exceed safe thresholds."""
            else:
                welcome_msg = f"""✅ You're already registered!

Chat ID: {chat_id}
Status: {"Active" if existing.is_active else "Inactive"}"""
            
            await telegram_service.send_alert(str(chat_id), welcome_msg)
        
        return {"ok": True}
        
    except Exception as e:
        return {"ok": False, "error": str(e)}
