"""
Alert API Endpoints - Production Postgres version
Optimized for Vercel Postgres with connection pooling
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
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

# =====================
# Recipients Management
# =====================

@router.post("/recipients", response_model=AlertRecipient, status_code=status.HTTP_201_CREATED)
async def create_recipient(recipient: AlertRecipient, db: Session = Depends(get_db)):
    """Add new alert recipient"""
    try:
        # Check if telegram_chat_id already exists
        if recipient.telegram_chat_id:
            existing = db.query(DBAlertRecipient).filter(
                DBAlertRecipient.telegram_chat_id == recipient.telegram_chat_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Telegram chat ID already registered"
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
    try:
        telegram_service = get_telegram_service()
        bot_info = await telegram_service.get_bot_info()
        bot_configured = bot_info is not None
        bot_username = bot_info.get('username') if bot_info else None
    except:
        bot_configured = False
        bot_username = None
    
    recipients = db.query(DBAlertRecipient).filter(DBAlertRecipient.is_active == True).all()
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
        "active_recipients": len(recipients),
        "total_alerts_sent": total_alerts
    }

# ===================
# Test Alert
# ===================

@router.post("/test")
async def send_test_alert(request: TestAlertRequest, db: Session = Depends(get_db)):
    """Send test alert to all active recipients"""
    try:
        telegram_service = get_telegram_service()
        bot_info = await telegram_service.get_bot_info()
        
        if not bot_info:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Telegram bot not configured"
            )
        
        recipients = db.query(DBAlertRecipient).filter(DBAlertRecipient.is_active == True).all()
        if not recipients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active recipients configured"
            )
        
        success_count = 0
        errors = []
        notified_ids = []
        
        message = request.message or f"""🧪 <b>Test Alert</b>

This is a test message from Evara TDS Platform.

✅ Bot: @{bot_info.get('username', 'Unknown')}
✅ Recipients: {len(recipients)}
✅ Alerts System: Online

<i>Sent at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</i>"""
        
        for recipient in recipients:
            if recipient.telegram_chat_id and 'telegram' in (recipient.channels or []):
                try:
                    await telegram_service.send_alert(recipient.telegram_chat_id, message)
                    success_count += 1
                    notified_ids.append(recipient.telegram_chat_id)
                except Exception as e:
                    errors.append(f"{recipient.name}: {str(e)}")
        
        # Log to history
        alert_history = DBAlertHistory(
            alert_type="test",
            severity="info",
            message=request.message or "Test alert",
            recipients_notified=notified_ids,
            channels_used=["telegram"],
            delivery_status={"success": success_count, "failed": len(errors)},
            recipient_count=len(recipients)
        )
        db.add(alert_history)
        db.commit()
        
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
