from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.api.v1.endpoints import router as api_router
from app.api.v1.users import router as users_router
from app.api.v1.alerts import router as alerts_router
from app.models.database import init_db

# Rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(title=settings.PROJECT_NAME)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security: Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app", "evaratds.com", "*.evaratds.com"]
)

# CORS Setup (Clerk + Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://evaratds.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")

# Initialize alert database
@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/health")
@limiter.limit("10/minute")
def health_check():
    return {"status": "active", "version": "3.0.0", "auth": "clerk"}

# Security headers middleware
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# To run: uvicorn main:app --reload
