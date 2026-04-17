"""DataPilot AI — FastAPI server entry point."""

import os
import pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from models.schemas import AnalyzeRequest, AnalyzeResponse, UploadResponse
from agent import DataPilotAgent
from tools.csv_loader import load_csv

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
CHART_OUTPUT_DIR = os.getenv("CHART_OUTPUT_DIR", "./outputs")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create required directories on startup."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(CHART_OUTPUT_DIR, exist_ok=True)
    os.makedirs("static", exist_ok=True)
    print("[START] DataPilot AI server started")
    print(f"   Uploads dir: {os.path.abspath(UPLOAD_DIR)}")
    print(f"   Charts dir:  {os.path.abspath(CHART_OUTPUT_DIR)}")
    yield
    print("[STOP] DataPilot AI server stopped")


app = FastAPI(
    title="DataPilot AI",
    description="Intelligent CSV analysis assistant powered by Claude LLM and MCP tools",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize agent
agent = DataPilotAgent()


# ─── Health Check ───────────────────────────────────────────────
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0"}


# ─── Upload CSV ─────────────────────────────────────────────────
@app.post("/upload", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file for analysis.
    Validates extension and file size, then saves to uploads directory.
    """
    # Validate extension
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted.")

    # Read file content
    content = await file.read()

    # Validate size
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File size ({file_size_mb:.1f} MB) exceeds the {MAX_FILE_SIZE_MB} MB limit.",
        )

    # Validate non-empty
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty (0 bytes).")

    # Save file
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        f.write(content)

    # Validate it's a readable CSV
    csv_info = load_csv(file.filename)
    if not csv_info.get("success"):
        # Clean up invalid file
        os.remove(filepath)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid CSV file: {csv_info.get('error', 'Could not parse the file.')}",
        )

    return UploadResponse(
        filename=file.filename,
        rows=csv_info["rows"],
        columns=csv_info["columns"],
        message=f"Successfully uploaded '{file.filename}' with {csv_info['rows']} rows and {len(csv_info['columns'])} columns.",
    )


# ─── Analyze ────────────────────────────────────────────────────
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Analyze uploaded CSV data using natural language queries.
    The LLM agent orchestrates tools to answer the question.
    """
    # Validate file exists
    filepath = os.path.join(UPLOAD_DIR, request.filename)
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail=f"File '{request.filename}' not found. Please upload it first.",
        )

    try:
        result = await agent.analyze(request.query, request.filename)
        return result
    except Exception as e:
        print(f"[ERROR] Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ─── Serve Chart Images ────────────────────────────────────────
@app.get("/chart/{filename}")
async def get_chart(filename: str):
    """Serve generated chart images from the outputs directory."""
    filepath = os.path.join(CHART_OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Chart '{filename}' not found.")
    return FileResponse(filepath, media_type="image/png")


# ─── Column Info ────────────────────────────────────────────────
@app.get("/columns/{filename}")
async def get_columns(filename: str):
    """Return column names and data types for a specific uploaded file."""
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")

    try:
        df = pd.read_csv(filepath, nrows=5)
        columns = [
            {"name": col, "dtype": str(dtype)}
            for col, dtype in df.dtypes.items()
        ]
        return {"filename": filename, "columns": columns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read columns: {str(e)}")


# ─── Serve Frontend ────────────────────────────────────────────
@app.get("/")
async def serve_frontend():
    """Serve the single-page frontend."""
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
