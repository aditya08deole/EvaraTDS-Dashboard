from fastapi import APIRouter, HTTPException
from app.services.thingspeak import fetch_evara_data
from app.schemas.sensor import DashboardData
from app.core.config import settings
from .recipients import router as recipients_router
from .settings import router as settings_router
from app.services.email_service import EmailAlertService
from app.database.db import RecipientDB, AlertLogDB
import json
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Include sub-routers
router.include_router(recipients_router, prefix="", tags=["recipients"])
router.include_router(settings_router, prefix="", tags=["settings"])

SETTINGS_FILE = "backend/data/settings.json"

def load_settings_file():
    """Load current settings"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {"tdsThreshold": 150, "tempThreshold": 35}

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_metrics():
    """
    Get dashboard metrics with ThingSpeak data and analysis
    
    1. Fetches raw data from ThingSpeak
    2. Runs analysis (Alert Logic)
    3. Returns clean JSON for React
    """
    raw_data = await fetch_evara_data(results=60)

    if isinstance(raw_data, dict) and raw_data.get("error"):
        raise HTTPException(status_code=502, detail="Upstream Data Error")

    latest = raw_data.get("latest")

    status = "NORMAL"
    if latest:
        try:
            if latest.get('tds', 0) > settings.TDS_ALERT_THRESHOLD:
                status = "CRITICAL"
            elif latest.get('tds', 0) > (settings.TDS_ALERT_THRESHOLD * 0.8):
                status = "WARNING"
        except Exception:
            status = "WARNING"

    return {
        "latest": latest,
        "history": raw_data.get("history", []),
        "system_status": status,
        "last_updated": latest.get("created_at") if latest else None
    }

@router.post("/check-alerts")
async def check_and_send_alerts():
    """
    Professional alert checker with database-backed recipients
    Called periodically from frontend
    """
    try:
        # Fetch latest sensor data
        data = await fetch_evara_data(results=1)
        if not data or not data.get("latest"):
            return {"message": "No data available", "status": "no_data"}
        
        latest = data["latest"]
        settings_data = load_settings_file()
        
        # Get recipients from database
        recipients = RecipientDB.get_all(active_only=True)
        
        if not recipients:
            return {"message": "No active recipients configured", "status": "no_recipients"}
        
        tds = latest.get("tds", 0)
        temp = latest.get("temp", 0)
        tds_threshold = settings_data.get("tdsThreshold", 150)
        temp_threshold = settings_data.get("tempThreshold", 35)
        
        alerts_sent = []
        
        # Check TDS threshold
        if tds > tds_threshold:
            success = await EmailAlertService.send_tds_alert(recipients, tds, tds_threshold)
            if success:
                alerts_sent.append(f"TDS alert sent ({tds:.1f} > {tds_threshold})")
        
        # Check Temperature threshold
        if temp > temp_threshold:
            success = await EmailAlertService.send_temp_alert(recipients, temp, temp_threshold)
            if success:
                alerts_sent.append(f"Temperature alert sent ({temp:.1f} > {temp_threshold})")
        
        if alerts_sent:
            logger.info(f"Alerts sent: {alerts_sent}")
            return {"message": "Alerts sent", "alerts": alerts_sent, "status": "sent"}
        else:
            return {
                "message": "No alerts needed", 
                "tds": tds, 
                "temp": temp,
                "status": "normal"
            }
    
    except Exception as e:
        logger.error(f"Error in check_alerts: {e}")
        return {"error": str(e), "status": "error"}

@router.get("/alert-history")
async def get_alert_history(limit: int = 10):
    """Get recent alert history from database"""
    try:
        logs = AlertLogDB.get_recent(limit=limit)
        logger.info(f"Retrieved {len(logs)} alert logs")
        return {
            "logs": logs,
            "count": len(logs)
        }
    except Exception as e:
        logger.error(f"Error fetching alert history: {e}")
        return {"error": str(e)}
