"""
Vercel Serverless Function Handler for FastAPI Backend
This allows the FastAPI app to run as a serverless function on Vercel
Includes cron job for automatic alerts
"""
from mangum import Mangum
from backend.main import app
from api.cron import router as cron_router

# Add cron router to main app
app.include_router(cron_router, prefix="/api/cron", tags=["cron"])

# Mangum adapter converts ASGI (FastAPI) to AWS Lambda/Vercel format
handler = Mangum(app, lifespan="off")
