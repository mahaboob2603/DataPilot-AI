"""Vercel serverless function entry point — wraps the FastAPI app."""

import sys
import os

# Add project root to Python path so all imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Vercel-specific environment variables (use /tmp for writable storage)
os.environ.setdefault("UPLOAD_DIR", "/tmp/uploads")
os.environ.setdefault("CHART_OUTPUT_DIR", "/tmp/outputs")
os.environ.setdefault("DB_PATH", "/tmp/datapilot.db")
os.environ.setdefault("VERCEL", "1")

# Ensure /tmp directories exist
os.makedirs("/tmp/uploads", exist_ok=True)
os.makedirs("/tmp/outputs", exist_ok=True)

# Import the FastAPI app from main.py — Vercel looks for `app`
from main import app
