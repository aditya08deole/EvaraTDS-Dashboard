"""
Alert API Endpoints - Secure recipient and alert management
All sensitive tokens are stored in environment variables only
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.alert import AlertRecipient, AlertHistory, AlertConfig, TestAlertRequest
from app.models.database import (
    get_db, 
    DBAlertRecipient, 
    DBAlertHistory, 
    DBAlertConfig,
    init_db
)
from app.services.alert_engine import AlertEngine
from app.services.telegram_service import get_telegram_service
import asyncio

router = APIRouter(prefix="/alerts", tags=["alerts"])

# Initialize database on startup
init_db()

# =====================
# Recipients Management
# =====================

@router.post("/recipients", response_model=AlertRecipient, status_code=status.HTTP_201_CREATED)
async def create_recipient(recipient: AlertRecipient, db: Session = Depends(get_db)):
    """
    Add new alert recipient
    
    To get Telegram chat_id:
    1. Send /start to your bot
    2. Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
    3. Look for "chat":{"id": 123456789}
    """
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
        is_active=recipient.is_active,
        channels=recipient.channels,
        created_by=recipient.created_by
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

@router.get("/recipients", response_model=List[AlertRecipient])
async def get_recipients(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all alert recipients"""
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
    """Get alert history with optional filtering"""
    query = db.query(DBAlertHistory).order_by(DBAlertHistory.created_at.desc())
    
    if alert_type:
        query = query.filter(DBAlertHistory.alert_type == alert_type)
    
    history = query.limit(limit).all()
    
    return [
        AlertHistory(
            id=h.id,
            alert_type=h.alert_type,
            tds_value=h.tds_value,
            threshold=h.threshold,
            message=h.message,
            recipients_notified=h.recipients_notified or [],
            channels_used=h.channels_used or [],
            delivery_status=h.delivery_status or {},
            created_at=h.created_at
        )
        for h in history
    ]

# ===================
# Configuration
# ===================

@router.get("/config", response_model=AlertConfig)
async def get_config(db: Session = Depends(get_db)):
    """Get current alert configuration"""
    config = db.query(DBAlertConfig).first()
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
    
    return AlertConfig(
        tds_threshold=config.tds_threshold,
        warning_threshold=config.warning_threshold,
        cooldown_minutes=config.cooldown_minutes,
        enable_telegram=config.telegram_enabled,
        enable_email=config.email_enabled,
        enable_sms=config.sms_enabled,
        offline_threshold_minutes=config.offline_threshold_minutes
    )

@router.put("/config", response_model=AlertConfig)
async def update_config(config_update: AlertConfig, db: Session = Depends(get_db)):
    """Update alert configuration"""
    config = db.query(DBAlertConfig).first()
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
    
    config.tds_threshold = config_update.tds_threshold
    config.temp_threshold = 35.0  # Default
    config.warning_threshold = config_update.warning_threshold
    config.cooldown_minutes = config_update.cooldown_minutes
    config.telegram_enabled = config_update.enable_telegram
    config.email_enabled = config_update.enable_email
    config.sms_enabled = config_update.enable_sms
    config.offline_threshold_minutes = config_update.offline_threshold_minutes
    config.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(config)
    
    return AlertConfig(
        tds_threshold=config.tds_threshold,
        warning_threshold=config.warning_threshold,
        cooldown_minutes=config.cooldown_minutes,
        enable_telegram=config.telegram_enabled,
        enable_email=config.email_enabled,
        enable_sms=config.sms_enabled,
        offline_threshold_minutes=config.offline_threshold_minutes
    )

# ===================
# Testing & Status
# ===================

@router.post("/test", status_code=status.HTTP_200_OK)
async def test_alert(test_request: TestAlertRequest, db: Session = Depends(get_db)):
    """
    Send test alert to recipients
    
    If recipient_ids provided, sends to those specific recipients.
    Otherwise sends to all active recipients.
    """
    telegram = get_telegram_service()
    
    # Verify bot is configured
    bot_info = await telegram.get_bot_info()
    if not bot_info:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram bot not configured. Set TELEGRAM_BOT_TOKEN in .env file"
        )
    
    # Get recipients
    query = db.query(DBAlertRecipient).filter(DBAlertRecipient.is_active == True)
    if test_request.recipient_ids:
        query = query.filter(DBAlertRecipient.id.in_(test_request.recipient_ids))
    
    recipients = query.all()
    
    if not recipients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active recipients found"
        )
    
    # Send test message
    test_message = f"""
🧪 <b>TEST ALERT</b>

{test_request.message}

<b>Bot Info:</b>
• Username: @{bot_info['username']}
• Name: {bot_info['first_name']}

<i>Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</i>
"""
    
    chat_ids = [r.telegram_chat_id for r in recipients if r.telegram_chat_id]
    results = await telegram.send_bulk_alert(chat_ids, test_message)
    
    return {
        "success": True,
        "message": "Test alert sent",
        "bot_username": bot_info['username'],
        "recipients_total": results['total'],
        "sent_successfully": results['success'],
        "failed": results['failed']
    }

@router.get("/status")
async def get_alert_status(db: Session = Depends(get_db)):
    """Get alert system status"""
    engine = AlertEngine(db)
    telegram = get_telegram_service()
    
    bot_info = await telegram.get_bot_info()
    
    return {
        **engine.get_alert_status(),
        "bot_configured": bot_info is not None,
        "bot_username": bot_info['username'] if bot_info else None,
        "active_recipients": db.query(DBAlertRecipient).filter(
            DBAlertRecipient.is_active == True
        ).count(),
        "total_alerts_sent": db.query(DBAlertHistory).count()
    }

@router.post("/check-sensor-data")
async def check_sensor_data(
    tds: float,
    temp: float,
    voltage: float,
    db: Session = Depends(get_db)
):
    """
    Check sensor data against thresholds and trigger alerts if needed
    
    This endpoint should be called by your data ingestion pipeline
    """
    engine = AlertEngine(db)
    result = await engine.process_sensor_data(tds, temp, voltage)
    
    if result:
        return {
            "alert_triggered": True,
            **result
        }
    else:
        return {
            "alert_triggered": False,
            "message": "All values within normal range"
        }
