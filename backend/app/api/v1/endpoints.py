from fastapi import APIRouter, HTTPException, Depends
from app.services.thingspeak import fetch_evara_data
from app.schemas.sensor import DashboardData
from app.core.config import settings
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_metrics(current_user: dict = Depends(get_current_user)):
    """
    Protected endpoint: Aggregates ThingSpeak data with analysis
    Requires valid Clerk authentication token
    
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
