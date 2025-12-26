"""
Vercel Serverless Function Handler for FastAPI Backend
This allows the FastAPI app to run as a serverless function on Vercel
"""
from mangum import Mangum
from backend.main import app

# Mangum adapter converts ASGI (FastAPI) to AWS Lambda/Vercel format
handler = Mangum(app, lifespan="off")
