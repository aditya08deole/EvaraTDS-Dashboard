"""
User Management Endpoints
Handles user synchronization and profile management with Clerk
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.core.auth import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])

# In-memory user storage (replace with database in production)
users_db = {}

class UserProfile(BaseModel):
    user_id: str
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: str = "viewer"
    created_at: datetime
    last_login: datetime

class UserSync(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None

@router.post("/sync", response_model=UserProfile)
async def sync_user(
    user_data: UserSync,
    current_user: dict = Depends(get_current_user)
):
    """
    Sync/upsert user from Clerk to internal database
    Called automatically on first login or profile update
    """
    user_id = current_user["user_id"]
    
    # Determine role
    role = "admin" if require_admin(current_user) else "viewer"
    
    # Upsert user
    if user_id in users_db:
        users_db[user_id]["last_login"] = datetime.utcnow()
        users_db[user_id]["email"] = user_data.email
        users_db[user_id]["username"] = user_data.username
        users_db[user_id]["full_name"] = user_data.full_name
        users_db[user_id]["role"] = role
    else:
        users_db[user_id] = {
            "user_id": user_id,
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
            "role": role,
            "created_at": datetime.utcnow(),
            "last_login": datetime.utcnow(),
        }
    
    return UserProfile(**users_db[user_id])

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user's profile"""
    user_id = current_user["user_id"]
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found. Please sync your profile.")
    
    return UserProfile(**users_db[user_id])

@router.get("/", response_model=list[UserProfile])
async def list_users(current_user: dict = Depends(get_current_user)):
    """List all users (admin only)"""
    if not require_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return [UserProfile(**user) for user in users_db.values()]
