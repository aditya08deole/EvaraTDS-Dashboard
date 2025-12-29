from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List
import json
import os
from datetime import datetime
import uuid

router = APIRouter()

RECIPIENTS_FILE = "backend/data/recipients.json"

class RecipientCreate(BaseModel):
    name: str
    email: EmailStr

class Recipient(BaseModel):
    id: str
    name: str
    email: str
    addedAt: str

def ensure_recipients_file():
    """Ensure the recipients file exists"""
    os.makedirs(os.path.dirname(RECIPIENTS_FILE), exist_ok=True)
    if not os.path.exists(RECIPIENTS_FILE):
        with open(RECIPIENTS_FILE, 'w') as f:
            json.dump([], f)

def load_recipients() -> List[Recipient]:
    """Load recipients from file"""
    ensure_recipients_file()
    try:
        with open(RECIPIENTS_FILE, 'r') as f:
            data = json.load(f)
            return [Recipient(**item) for item in data]
    except Exception as e:
        print(f"Error loading recipients: {e}")
        return []

def save_recipients(recipients: List[Recipient]):
    """Save recipients to file"""
    ensure_recipients_file()
    with open(RECIPIENTS_FILE, 'w') as f:
        json.dump([r.dict() for r in recipients], f, indent=2)

@router.get("/recipients", response_model=List[Recipient])
async def get_recipients():
    """Get all recipients"""
    return load_recipients()

@router.post("/recipients", response_model=Recipient)
async def add_recipient(recipient_data: RecipientCreate):
    """Add a new recipient"""
    recipients = load_recipients()
    
    # Check if email already exists
    for r in recipients:
        if r.email.lower() == recipient_data.email.lower():
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create new recipient
    new_recipient = Recipient(
        id=str(uuid.uuid4()),
        name=recipient_data.name,
        email=recipient_data.email,
        addedAt=datetime.utcnow().isoformat()
    )
    
    recipients.append(new_recipient)
    save_recipients(recipients)
    
    return new_recipient

@router.delete("/recipients/{recipient_id}")
async def delete_recipient(recipient_id: str):
    """Delete a recipient"""
    recipients = load_recipients()
    
    # Find and remove recipient
    original_count = len(recipients)
    recipients = [r for r in recipients if r.id != recipient_id]
    
    if len(recipients) == original_count:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    save_recipients(recipients)
    
    return {"message": "Recipient deleted successfully"}
