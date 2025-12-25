"""
Serverless-compatible storage adapter
Falls back to JSON storage when SQLite is not available (Vercel serverless)
"""
import os
import json
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from app.models.alert import AlertRecipient, AlertHistory, AlertConfig

# Storage path for JSON fallback
STORAGE_DIR = Path("/tmp") if os.environ.get("VERCEL") else Path("backend/data")
STORAGE_DIR.mkdir(exist_ok=True, parents=True)

RECIPIENTS_FILE = STORAGE_DIR / "recipients.json"
HISTORY_FILE = STORAGE_DIR / "alert_history.json"
CONFIG_FILE = STORAGE_DIR / "config.json"

class ServerlessStorage:
    """JSON-based storage for serverless environments"""
    
    @staticmethod
    def _load_json(file_path: Path) -> List[Dict]:
        """Load JSON file"""
        if not file_path.exists():
            return []
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except:
            return []
    
    @staticmethod
    def _save_json(file_path: Path, data: List[Dict]):
        """Save to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # Recipients
    @staticmethod
    def add_recipient(recipient: AlertRecipient) -> AlertRecipient:
        """Add new recipient"""
        recipients = ServerlessStorage._load_json(RECIPIENTS_FILE)
        
        # Check if telegram_chat_id already exists
        if recipient.telegram_chat_id:
            existing = [r for r in recipients if r.get('telegram_chat_id') == recipient.telegram_chat_id]
            if existing:
                raise ValueError("Telegram chat ID already registered")
        
        # Generate ID
        max_id = max([r.get('id', 0) for r in recipients], default=0)
        recipient_dict = {
            'id': max_id + 1,
            'name': recipient.name,
            'telegram_chat_id': recipient.telegram_chat_id,
            'email': recipient.email,
            'phone': recipient.phone,
            'role': recipient.role,
            'is_active': recipient.is_active,
            'channels': recipient.channels,
            'created_at': datetime.utcnow().isoformat(),
            'created_by': recipient.created_by
        }
        
        recipients.append(recipient_dict)
        ServerlessStorage._save_json(RECIPIENTS_FILE, recipients)
        
        return AlertRecipient(**recipient_dict)
    
    @staticmethod
    def get_recipients(active_only: bool = True) -> List[AlertRecipient]:
        """Get all recipients"""
        recipients = ServerlessStorage._load_json(RECIPIENTS_FILE)
        
        if active_only:
            recipients = [r for r in recipients if r.get('is_active', True)]
        
        return [AlertRecipient(**r) for r in recipients]
    
    @staticmethod
    def get_recipient_by_id(recipient_id: int) -> Optional[AlertRecipient]:
        """Get recipient by ID"""
        recipients = ServerlessStorage._load_json(RECIPIENTS_FILE)
        recipient = next((r for r in recipients if r.get('id') == recipient_id), None)
        return AlertRecipient(**recipient) if recipient else None
    
    @staticmethod
    def update_recipient(recipient_id: int, updates: Dict) -> Optional[AlertRecipient]:
        """Update recipient"""
        recipients = ServerlessStorage._load_json(RECIPIENTS_FILE)
        
        for i, r in enumerate(recipients):
            if r.get('id') == recipient_id:
                recipients[i].update(updates)
                ServerlessStorage._save_json(RECIPIENTS_FILE, recipients)
                return AlertRecipient(**recipients[i])
        
        return None
    
    @staticmethod
    def delete_recipient(recipient_id: int) -> bool:
        """Delete recipient"""
        recipients = ServerlessStorage._load_json(RECIPIENTS_FILE)
        original_len = len(recipients)
        recipients = [r for r in recipients if r.get('id') != recipient_id]
        
        if len(recipients) < original_len:
            ServerlessStorage._save_json(RECIPIENTS_FILE, recipients)
            return True
        return False
    
    # Alert History
    @staticmethod
    def add_alert_history(alert: AlertHistory) -> AlertHistory:
        """Log alert to history"""
        history = ServerlessStorage._load_json(HISTORY_FILE)
        
        max_id = max([h.get('id', 0) for h in history], default=0)
        alert_dict = {
            'id': max_id + 1,
            'alert_type': alert.alert_type,
            'severity': alert.severity,
            'message': alert.message,
            'tds_value': alert.tds_value,
            'temp_value': alert.temp_value,
            'voltage_value': alert.voltage_value,
            'threshold': alert.threshold,
            'recipients_notified': alert.recipients_notified,
            'channels_used': alert.channels_used,
            'delivery_status': alert.delivery_status,
            'recipient_count': alert.recipient_count,
            'created_at': datetime.utcnow().isoformat()
        }
        
        history.append(alert_dict)
        # Keep only last 1000 alerts
        history = history[-1000:]
        ServerlessStorage._save_json(HISTORY_FILE, history)
        
        return AlertHistory(**alert_dict)
    
    @staticmethod
    def get_alert_history(limit: int = 50) -> List[AlertHistory]:
        """Get recent alert history"""
        history = ServerlessStorage._load_json(HISTORY_FILE)
        history = sorted(history, key=lambda x: x.get('created_at', ''), reverse=True)
        return [AlertHistory(**h) for h in history[:limit]]
    
    # Config
    @staticmethod
    def get_config() -> Optional[AlertConfig]:
        """Get alert configuration"""
        configs = ServerlessStorage._load_json(CONFIG_FILE)
        if configs:
            return AlertConfig(**configs[0])
        return None
    
    @staticmethod
    def update_config(config: AlertConfig) -> AlertConfig:
        """Update configuration"""
        config_dict = {
            'id': 1,
            'tds_threshold': config.tds_threshold,
            'warning_threshold': config.warning_threshold,
            'cooldown_minutes': config.cooldown_minutes,
            'enable_telegram': config.enable_telegram,
            'enable_email': config.enable_email,
            'enable_sms': config.enable_sms,
            'enabled': config.enabled
        }
        
        ServerlessStorage._save_json(CONFIG_FILE, [config_dict])
        return AlertConfig(**config_dict)
