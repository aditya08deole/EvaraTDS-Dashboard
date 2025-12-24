"""
Clerk JWT Authentication Middleware
Verifies Clerk session tokens and extracts user information
"""
import os
from typing import Optional
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient
from functools import lru_cache

security = HTTPBearer()

# Clerk configuration
CLERK_JWKS_URL = f"https://{os.getenv('CLERK_DOMAIN', 'awake-wahoo-64.clerk.accounts.dev')}/.well-known/jwks.json"
CLERK_ISSUER = f"https://{os.getenv('CLERK_DOMAIN', 'awake-wahoo-64.clerk.accounts.dev')}"

@lru_cache()
def get_jwks_client():
    """Cache JWKS client to avoid repeated fetches"""
    return PyJWKClient(CLERK_JWKS_URL)

def verify_clerk_token(token: str) -> dict:
    """
    Verify Clerk JWT token and return decoded payload
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Decoded token payload with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Decode and verify token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=CLERK_ISSUER,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": False,  # Clerk doesn't always include aud
            }
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token verification failed: {str(e)}"
        )

async def get_current_user(request: Request) -> dict:
    """
    FastAPI dependency to extract and verify user from request
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user_id": user["sub"]}
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.split(" ")[1]
    payload = verify_clerk_token(token)
    
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "email_verified": payload.get("email_verified", False),
        "username": payload.get("username"),
        "metadata": payload.get("public_metadata", {}),
    }

def require_admin(user: dict) -> bool:
    """
    Check if user has admin role
    
    Usage:
        @app.post("/admin-only")
        async def admin_route(user: dict = Depends(get_current_user)):
            if not require_admin(user):
                raise HTTPException(403, "Admin access required")
    """
    metadata = user.get("metadata", {})
    role = metadata.get("role", "")
    email = user.get("email", "")
    
    return role == "admin" or email.endswith("@evaratds.com")
