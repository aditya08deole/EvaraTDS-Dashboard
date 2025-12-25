"""
SQLAlchemy Database Models for Alert System
Stores alert configuration, recipients, and history in SQLite
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class DBAlertRecipient(Base):
    """Stores alert recipient contact information"""
    __tablename__ = "alert_recipients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    telegram_chat_id = Column(String(50), unique=True, index=True)
    email = Column(String(100))
    phone = Column(String(20))
    role = Column(String(20), default="viewer")  # 'admin' or 'viewer'
    is_active = Column(Boolean, default=True)
    channels = Column(JSON, default=["telegram"])  # ['telegram', 'email', 'sms']
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50))

class DBAlertHistory(Base):
    """Logs all alerts sent"""
    __tablename__ = "alert_history"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)  # 'critical', 'warning', 'recovery'
    severity = Column(String(20), nullable=False)  # 'critical', 'warning', 'info'
    message = Column(String(500), nullable=False)
    tds_value = Column(Float)
    temp_value = Column(Float)
    voltage_value = Column(Float)
    threshold = Column(Float)
    recipients_notified = Column(JSON, default=[])
    channels_used = Column(JSON, default=[])
    delivery_status = Column(JSON, default={})
    recipient_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class DBAlertConfig(Base):
    """System-wide alert configuration"""
    __tablename__ = "alert_config"
    
    id = Column(Integer, primary_key=True)
    tds_threshold = Column(Float, default=150.0)
    temp_threshold = Column(Float, default=35.0)
    warning_threshold = Column(Float, default=135.0)  # 90% of critical
    cooldown_minutes = Column(Integer, default=15)
    telegram_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=False)
    sms_enabled = Column(Boolean, default=False)
    offline_threshold_minutes = Column(Integer, default=5)
    last_alert_time = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database initialization
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./alerts.db")
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database with tables"""
    Base.metadata.create_all(bind=engine)
    
    # Create default config if not exists
    db = SessionLocal()
    try:
        config = db.query(DBAlertConfig).first()
        if not config:
            default_config = DBAlertConfig(
                tds_threshold=float(os.getenv("TDS_ALERT_THRESHOLD", 150.0)),
                temp_threshold=float(os.getenv("TEMP_ALERT_THRESHOLD", 35.0)),
                cooldown_minutes=int(os.getenv("ALERT_COOLDOWN_MINUTES", 15))
            )
            db.add(default_config)
            db.commit()
    finally:
        db.close()

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
