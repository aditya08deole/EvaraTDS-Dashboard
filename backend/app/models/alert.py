"""
Alert System Database Models
Handles recipients, alert history, and configuration
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import json

# ===========================
# Pydantic Models (API)
# ===========================

class AlertRecipient(BaseModel):
    id: Optional[int] = None
    name: str
    telegram_chat_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = "viewer"  # 'admin' or 'viewer'
    is_active: bool = True
    channels: List[str] = ["telegram"]  # ['telegram', 'email', 'sms']
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None

class AlertHistory(BaseModel):
    id: Optional[int] = None
    alert_type: str  # 'critical', 'warning', 'recovery', 'offline'
    tds_value: float
    threshold: float
    message: str
    recipients_notified: List[str] = []
    channels_used: List[str] = []
    delivery_status: dict = {}
    created_at: Optional[datetime] = None

class AlertConfig(BaseModel):
    tds_threshold: float = 150.0
    warning_threshold: float = 135.0  # 90% of critical
    cooldown_minutes: int = 5
    enable_telegram: bool = True
    enable_email: bool = False
    enable_sms: bool = False
    telegram_bot_token: Optional[str] = None
    email_from: str = "alerts@evaratds.com"
    offline_threshold_minutes: int = 5

class TestAlertRequest(BaseModel):
    recipient_ids: Optional[List[int]] = None  # If None, send to all active
    message: str = "This is a test alert from EvaraTDS system."

class AlertStats(BaseModel):
    total_alerts: int = 0
    critical_alerts: int = 0
    warning_alerts: int = 0
    recovery_alerts: int = 0
    active_recipients: int = 0
    last_alert: Optional[datetime] = None
    uptime_percentage: float = 100.0

# ===========================
# Database Helper (SQLite)
# ===========================

class AlertDatabase:
    """In-memory storage for MVP (can upgrade to SQLite/Postgres later)"""
    
    def __init__(self):
        self.recipients: List[AlertRecipient] = []
        self.alert_history: List[AlertHistory] = []
        self.config = AlertConfig()
        self.last_alert_time = {}  # recipient_id -> timestamp (for cooldown)
        self._next_recipient_id = 1
        self._next_alert_id = 1
    
    # Recipients CRUD
    def add_recipient(self, recipient: AlertRecipient) -> AlertRecipient:
        recipient.id = self._next_recipient_id
        recipient.created_at = datetime.now()
        self.recipients.append(recipient)
        self._next_recipient_id += 1
        return recipient
    
    def get_recipients(self, active_only: bool = False) -> List[AlertRecipient]:
        if active_only:
            return [r for r in self.recipients if r.is_active]
        return self.recipients
    
    def get_recipient_by_id(self, recipient_id: int) -> Optional[AlertRecipient]:
        for r in self.recipients:
            if r.id == recipient_id:
                return r
        return None
    
    def get_recipient_by_chat_id(self, chat_id: str) -> Optional[AlertRecipient]:
        for r in self.recipients:
            if r.telegram_chat_id == chat_id:
                return r
        return None
    
    def update_recipient(self, recipient_id: int, updates: dict) -> Optional[AlertRecipient]:
        recipient = self.get_recipient_by_id(recipient_id)
        if recipient:
            for key, value in updates.items():
                if hasattr(recipient, key):
                    setattr(recipient, key, value)
        return recipient
    
    def delete_recipient(self, recipient_id: int) -> bool:
        self.recipients = [r for r in self.recipients if r.id != recipient_id]
        return True
    
    # Alert History
    def add_alert(self, alert: AlertHistory) -> AlertHistory:
        alert.id = self._next_alert_id
        alert.created_at = datetime.now()
        self.alert_history.append(alert)
        self._next_alert_id += 1
        
        # Keep only last 1000 alerts
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        return alert
    
    def get_alert_history(self, limit: int = 100) -> List[AlertHistory]:
        return sorted(self.alert_history, key=lambda x: x.created_at, reverse=True)[:limit]
    
    # Configuration
    def get_config(self) -> AlertConfig:
        return self.config
    
    def update_config(self, updates: dict) -> AlertConfig:
        for key, value in updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        return self.config
    
    # Cooldown Management
    def can_send_alert(self, recipient_id: int) -> bool:
        """Check if enough time has passed since last alert (cooldown)"""
        if recipient_id not in self.last_alert_time:
            return True
        
        last_time = self.last_alert_time[recipient_id]
        elapsed_minutes = (datetime.now() - last_time).total_seconds() / 60
        
        return elapsed_minutes >= self.config.cooldown_minutes
    
    def mark_alert_sent(self, recipient_id: int):
        """Record that an alert was sent to this recipient"""
        self.last_alert_time[recipient_id] = datetime.now()
    
    # Statistics
    def get_stats(self) -> AlertStats:
        stats = AlertStats()
        stats.total_alerts = len(self.alert_history)
        stats.critical_alerts = len([a for a in self.alert_history if a.alert_type == 'critical'])
        stats.warning_alerts = len([a for a in self.alert_history if a.alert_type == 'warning'])
        stats.recovery_alerts = len([a for a in self.alert_history if a.alert_type == 'recovery'])
        stats.active_recipients = len([r for r in self.recipients if r.is_active])
        
        if self.alert_history:
            stats.last_alert = max(a.created_at for a in self.alert_history)
        
        return stats

# Global database instance
alert_db = AlertDatabase()
