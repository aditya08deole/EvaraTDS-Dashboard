"""
Alert Engine - Core monitoring and alerting logic
Handles threshold monitoring, cooldown, and alert triggering
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.models.database import DBAlertHistory, DBAlertConfig, DBAlertRecipient
from app.services.telegram_service import get_telegram_service
import asyncio
import logging

logger = logging.getLogger(__name__)

class AlertEngine:
    """Core alert monitoring and triggering engine"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.telegram = get_telegram_service()
        self.config = self._load_config()
    
    def _load_config(self) -> DBAlertConfig:
        """Load alert configuration from database"""
        config = self.db.query(DBAlertConfig).first()
        if not config:
            # Create default config
            config = DBAlertConfig(
                tds_threshold=float(os.getenv("TDS_ALERT_THRESHOLD", 150.0)),
                temp_threshold=float(os.getenv("TEMP_ALERT_THRESHOLD", 35.0)),
                cooldown_minutes=int(os.getenv("ALERT_COOLDOWN_MINUTES", 15))
            )
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        return config
    
    def check_thresholds(self, tds: float, temp: float, voltage: float) -> Optional[Dict]:
        """
        Check if sensor values exceed thresholds
        
        Returns:
            dict with alert info if threshold exceeded, None otherwise
        """
        alert_info = None
        
        # Check TDS threshold
        if tds > self.config.tds_threshold:
            alert_info = {
                'type': 'high_tds',
                'severity': 'critical',
                'threshold': self.config.tds_threshold,
                'current_value': tds,
                'parameter': 'TDS'
            }
        
        # Check temperature threshold
        elif temp > self.config.temp_threshold:
            alert_info = {
                'type': 'high_temp',
                'severity': 'warning',
                'threshold': self.config.temp_threshold,
                'current_value': temp,
                'parameter': 'Temperature'
            }
        
        # Check low voltage
        elif voltage < 3.0:
            alert_info = {
                'type': 'low_voltage',
                'severity': 'warning',
                'threshold': 3.0,
                'current_value': voltage,
                'parameter': 'Voltage'
            }
        
        return alert_info
    
    def should_send_alert(self) -> bool:
        """Check if enough time has passed since last alert (cooldown)"""
        if not self.config.last_alert_time:
            return True
        
        time_since_last = datetime.utcnow() - self.config.last_alert_time
        cooldown_delta = timedelta(minutes=self.config.cooldown_minutes)
        
        return time_since_last >= cooldown_delta
    
    async def trigger_alert(
        self, 
        alert_type: str, 
        severity: str,
        tds: float, 
        temp: float, 
        voltage: float,
        threshold: float
    ) -> Dict:
        """
        Trigger an alert and send to all active recipients
        
        Returns:
            dict: Alert execution results
        """
        # Check cooldown
        if not self.should_send_alert():
            time_left = self._get_cooldown_remaining()
            logger.info(f"Alert suppressed due to cooldown. {time_left} minutes remaining.")
            return {
                'sent': False,
                'reason': 'cooldown',
                'time_remaining_minutes': time_left,
                'recipients': 0
            }
        
        # Get active recipients
        recipients = self.db.query(DBAlertRecipient).filter(
            DBAlertRecipient.is_active == True,
            DBAlertRecipient.telegram_chat_id.isnot(None)
        ).all()
        
        if not recipients:
            logger.warning("No active recipients configured for alerts")
            return {
                'sent': False,
                'reason': 'no_recipients',
                'recipients': 0
            }
        
        # Format alert message
        message = self.telegram.format_alert_message(
            alert_type=alert_type,
            tds=tds,
            temp=temp,
            voltage=voltage,
            threshold=threshold
        )
        
        # Send to all recipients
        chat_ids = [r.telegram_chat_id for r in recipients if r.telegram_chat_id]
        delivery_results = await self.telegram.send_bulk_alert(chat_ids, message)
        
        # Log alert in database
        alert_log = DBAlertHistory(
            alert_type=alert_type,
            severity=severity,
            message=message,
            tds_value=tds,
            temp_value=temp,
            voltage_value=voltage,
            threshold=threshold,
            recipients_notified=[r.name for r in recipients],
            channels_used=['telegram'],
            delivery_status={'success': delivery_results['success'], 'failed': delivery_results['failed']},
            recipient_count=delivery_results['success']
        )
        self.db.add(alert_log)
        
        # Update last alert time
        self.config.last_alert_time = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Alert triggered: {alert_type} | Sent to {delivery_results['success']}/{delivery_results['total']} recipients")
        
        return {
            'sent': True,
            'alert_type': alert_type,
            'severity': severity,
            'recipients': delivery_results['success'],
            'failed': delivery_results['failed'],
            'total': delivery_results['total'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _get_cooldown_remaining(self) -> float:
        """Get remaining cooldown time in minutes"""
        if not self.config.last_alert_time:
            return 0.0
        
        time_since_last = datetime.utcnow() - self.config.last_alert_time
        cooldown_delta = timedelta(minutes=self.config.cooldown_minutes)
        remaining = cooldown_delta - time_since_last
        
        return max(0.0, remaining.total_seconds() / 60)
    
    async def process_sensor_data(self, tds: float, temp: float, voltage: float) -> Optional[Dict]:
        """
        Main processing function - checks thresholds and triggers alerts
        
        Call this function every time new sensor data arrives
        """
        alert_info = self.check_thresholds(tds, temp, voltage)
        
        if alert_info:
            logger.info(f"Threshold exceeded: {alert_info['parameter']} = {alert_info['current_value']} (threshold: {alert_info['threshold']})")
            
            result = await self.trigger_alert(
                alert_type=alert_info['type'],
                severity=alert_info['severity'],
                tds=tds,
                temp=temp,
                voltage=voltage,
                threshold=alert_info['threshold']
            )
            return result
        
        return None
    
    def get_alert_status(self) -> Dict:
        """Get current alert system status"""
        return {
            'telegram_enabled': self.config.telegram_enabled,
            'tds_threshold': self.config.tds_threshold,
            'temp_threshold': self.config.temp_threshold,
            'cooldown_minutes': self.config.cooldown_minutes,
            'last_alert': self.config.last_alert_time.isoformat() if self.config.last_alert_time else None,
            'cooldown_remaining': self._get_cooldown_remaining(),
            'can_send_alert': self.should_send_alert()
        }
