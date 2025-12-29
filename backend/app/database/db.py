"""
Professional SQLite database for recipients and alert logs
Thread-safe, serverless-ready, with proper migrations
"""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional, Dict
import json

# Get absolute path relative to this file (works locally and on Vercel)
_DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = str(_DB_DIR / "evara_alerts.db")

def init_database():
    """Initialize database with schema (idempotent)"""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Recipients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipients (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                added_at TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Alert logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                value REAL NOT NULL,
                threshold REAL NOT NULL,
                recipients TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                method TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        
        # Index for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alert_logs_type_sent 
            ON alert_logs(alert_type, sent_at DESC)
        """)
        
        conn.commit()

@contextmanager
def get_db_connection():
    """Thread-safe database connection context manager"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

class RecipientDB:
    """Professional recipient management with database"""
    
    @staticmethod
    def add(recipient_id: str, name: str, email: str) -> bool:
        """Add new recipient"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO recipients (id, name, email, added_at) VALUES (?, ?, ?, ?)",
                    (recipient_id, name, email, datetime.utcnow().isoformat())
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    @staticmethod
    def get_all(active_only: bool = True) -> List[Dict]:
        """Get all recipients"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM recipients"
            if active_only:
                query += " WHERE is_active = 1"
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def delete(recipient_id: str) -> bool:
        """Soft delete recipient"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE recipients SET is_active = 0 WHERE id = ?",
                (recipient_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def exists(email: str) -> bool:
        """Check if email exists"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM recipients WHERE email = ? AND is_active = 1",
                (email,)
            )
            return cursor.fetchone() is not None

class AlertLogDB:
    """Professional alert logging with database"""
    
    @staticmethod
    def add(alert_type: str, value: float, threshold: float, 
            recipients: List[str], method: str, status: str = "success") -> None:
        """Log alert send attempt"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO alert_logs 
                   (alert_type, value, threshold, recipients, sent_at, method, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (alert_type, value, threshold, json.dumps(recipients),
                 datetime.utcnow().isoformat(), method, status)
            )
            conn.commit()
    
    @staticmethod
    def get_last_alert(alert_type: str) -> Optional[Dict]:
        """Get last successful alert of specific type"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM alert_logs 
                   WHERE alert_type = ? AND status = 'success'
                   ORDER BY sent_at DESC LIMIT 1""",
                (alert_type,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def get_recent(limit: int = 10) -> List[Dict]:
        """Get recent alert logs"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM alert_logs 
                   ORDER BY sent_at DESC LIMIT ?""",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def cleanup_old(days: int = 30) -> int:
        """Delete logs older than specified days"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cutoff = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            cursor.execute(
                "DELETE FROM alert_logs WHERE sent_at < datetime('now', '-' || ? || ' days')",
                (days,)
            )
            conn.commit()
            return cursor.rowcount

# Initialize database on module import
init_database()
init_database()
