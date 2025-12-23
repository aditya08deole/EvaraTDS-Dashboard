from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import router as api_router

app = FastAPI(title=settings.PROJECT_NAME)

# CORS Setup (Allow React to talk to Python)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Secure this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status": "active", "version": "2.0.0"}

# To run: uvicorn main:app --reload
