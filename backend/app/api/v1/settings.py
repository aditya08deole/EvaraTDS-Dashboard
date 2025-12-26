"""
Settings API - Global Calibration Management
Stores settings in JSON file for cross-device sync
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json
import os
from pathlib import Path

router = APIRouter()

# Settings file path
SETTINGS_FILE = Path(__file__).parent.parent.parent.parent / "data" / "settings.json"

# Ensure directory exists
SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

class SystemSettings(BaseModel):
    tdsThreshold: float = 150
    tempThreshold: float = 35
    alertEmail: str = ""
    refreshInterval: int = 3000
    lastModified: str = None
    modifiedBy: str = "system"

DEFAULT_SETTINGS = SystemSettings(lastModified=datetime.now().isoformat())

def load_settings() -> SystemSettings:
    """Load settings from JSON file"""
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                return SystemSettings(**data)
        else:
            # Create default settings file if it doesn't exist
            save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS

def save_settings(settings: SystemSettings):
    """Save settings to JSON file"""
    try:
        # Ensure directory exists
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings.dict(), f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save settings: {str(e)}")

@router.get("/settings")
async def get_settings():
    """Get current system settings"""
    settings = load_settings()
    return {
        "status": "success",
        "settings": settings.dict()
    }

@router.post("/settings")
async def update_settings(settings: SystemSettings):
    """Update system settings"""
    try:
        # Add timestamp and save
        settings.lastModified = datetime.now().isoformat()
        save_settings(settings)
        
        return {
            "status": "success",
            "message": "Settings updated successfully",
            "settings": settings.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/settings/reset")
async def reset_settings():
    """Reset settings to defaults"""
    try:
        default = DEFAULT_SETTINGS.copy()
        default.lastModified = datetime.now().isoformat()
        save_settings(default)
        
        return {
            "status": "success",
            "message": "Settings reset to defaults",
            "settings": default.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
