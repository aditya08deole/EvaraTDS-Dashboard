"""
Professional Recipients API with SQLite database
RESTful CRUD operations for email alert recipients
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List
import uuid
import logging

# Import database layer
try:
    from app.database.db import RecipientDB
except ImportError:
    from database.db import RecipientDB

logger = logging.getLogger(__name__)

router = APIRouter()


class RecipientCreate(BaseModel):
    """Request model for creating recipient"""
    name: str
    email: EmailStr


class Recipient(BaseModel):
    """Response model for recipient"""
    id: str
    name: str
    email: str
    added_at: str
    is_active: int = 1


@router.get("/recipients", response_model=List[Recipient])
async def get_recipients():
    """Get all active recipients"""
    try:
        recipients = RecipientDB.get_all(active_only=True)
        logger.info(f"Retrieved {len(recipients)} recipients")
        return recipients
    except Exception as e:
        logger.error(f"Error fetching recipients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recipients"
        )


@router.post("/recipients", response_model=Recipient, status_code=status.HTTP_201_CREATED)
async def add_recipient(recipient_data: RecipientCreate):
    """Add a new recipient"""
    try:
        # Check if email already exists
        if RecipientDB.exists(recipient_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {recipient_data.email} already exists"
            )
        
        # Create new recipient
        recipient_id = str(uuid.uuid4())
        success = RecipientDB.add(
            recipient_id,
            recipient_data.name,
            recipient_data.email
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add recipient"
            )
        
        # Return created recipient
        recipients = RecipientDB.get_all()
        new_recipient = next((r for r in recipients if r['id'] == recipient_id), None)
        
        logger.info(f"Added recipient: {recipient_data.email}")
        return new_recipient
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding recipient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add recipient"
        )


@router.delete("/recipients/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipient(recipient_id: str):
    """Delete (soft delete) a recipient"""
    try:
        success = RecipientDB.delete(recipient_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient not found"
            )
        
        logger.info(f"Deleted recipient: {recipient_id}")
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting recipient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete recipient"
        )
