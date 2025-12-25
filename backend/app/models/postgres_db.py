"""
Database configuration for PostgreSQL (Vercel Postgres)
Uses connection pooling for serverless environments
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Generator

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# For local development without Postgres, use SQLite
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./backend/data/alerts.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Vercel Postgres URL format
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class DBAlertRecipient(Base):
    __tablename__ = "alert_recipients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    telegram_chat_id = Column(String(100), unique=True, index=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    role = Column(String(50), default="viewer")
    is_active = Column(Boolean, default=True)
    channels = Column(JSON, default=list)  # ["telegram", "email", "sms"]
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True)

class DBAlertHistory(Base):
    __tablename__ = "alert_history"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)  # "tds", "temperature", "test"
    severity = Column(String(20), default="warning")  # "info", "warning", "critical"
    message = Column(String(1000), nullable=False)
    tds_value = Column(Float, nullable=True)
    temp_value = Column(Float, nullable=True)
    voltage_value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    recipients_notified = Column(JSON, default=list)
    channels_used = Column(JSON, default=list)
    delivery_status = Column(JSON, default=dict)
    recipient_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class DBAlertConfig(Base):
    __tablename__ = "alert_config"
    
    id = Column(Integer, primary_key=True)
    tds_threshold = Column(Float, default=150.0)
    temp_threshold = Column(Float, default=35.0)
    warning_threshold = Column(Float, default=120.0)
    cooldown_minutes = Column(Integer, default=15)
    enable_telegram = Column(Boolean, default=True)
    enable_email = Column(Boolean, default=False)
    enable_sms = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        
        # Create default config if not exists
        db = SessionLocal()
        try:
            config = db.query(DBAlertConfig).first()
            if not config:
                default_config = DBAlertConfig(
                    tds_threshold=150.0,
                    temp_threshold=35.0,
                    warning_threshold=120.0,
                    cooldown_minutes=15,
                    enabled=True
                )
                db.add(default_config)
                db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

def get_db() -> Generator:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
