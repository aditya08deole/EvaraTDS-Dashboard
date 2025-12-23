from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# Base Schema (Shared properties)
class ReadingBase(BaseModel):
    tds: float
    temp: float
    voltage: float
    created_at: datetime


# Schema for reading data from ThingSpeak
class ReadingCreate(ReadingBase):
    entry_id: int


# Schema for sending data to Frontend
class DashboardData(BaseModel):
    latest: Optional[ReadingBase]
    history: List[ReadingBase]
    system_status: str
    last_updated: datetime
