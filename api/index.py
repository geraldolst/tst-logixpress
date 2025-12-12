"""
Vercel serverless function handler for FastAPI
"""
from app.main import app

# This is the handler that Vercel will call
handler = app
