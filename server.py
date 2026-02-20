"""
Auto-Analyst AI — FastAPI Backend Server
REST API wrapping the LangGraph agent for the React frontend.

Endpoints:
    POST /api/upload    — Upload CSV, get data preview
    POST /api/analyze   — Run agent pipeline, get insight + charts
    GET  /api/charts/{filename} — Serve generated chart images

Run: python server.py
"""

import os
import sys
import glob
import shutil
import pandas as pd
from io import StringIO

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.graph import app as agent_app

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APP SETUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
api = FastAPI(
    title="Auto-Analyst AI",
    description="Autonomous Data Analysis Agent API",
    version="1.0.0"
)

# CORS — Allow React dev server
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = os.path.join("data", "input")
CHART_DIR = "."  # Charts are saved in project root by the agent
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINT: Upload CSV
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@api.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a CSV file and return a data preview."""
    try:
        # Save file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Read preview
        df = pd.read_csv(file_path)
        
        # Column info
        columns_info = []
        for col in df.columns:
            columns_info.append({
                "name": col,
                "dtype": str(df[col].dtype),
                "non_null": int(df[col].notna().sum()),
                "unique": int(df[col].nunique()),
                "sample": str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else "N/A"
            })
        
        return {
            "success": True,
            "filename": file.filename,
            "filepath": file_path,
            "rows": df.shape[0],
            "cols": df.shape[1],
            "columns": columns_info,
            "preview": df.head(8).to_dict(orient="records"),
            "column_names": list(df.columns)
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINT: Analyze Data
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@api.post("/api/analyze")
async def analyze_data(
    filepath: str = Form(...),
    query: str = Form(...)
):
    """Run the full agent pipeline and return results."""
    
    if not os.path.exists(filepath):
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": f"File not found: {filepath}"}
        )
    
    # Clean old charts
    for f in glob.glob("output*.png"):
        try:
            os.remove(f)
        except OSError:
            pass
    
    # Run agent
    initial_state = {
        "csv_file_path": filepath,
        "user_query": query,
        "revision_count": 0,
        "messages": []
    }
    
    final_state = {}
    node_log = []
    
    try:
        for output in agent_app.stream(initial_state):
            for node_name, state_update in output.items():
                if state_update is None:
                    continue
                final_state.update(state_update)
                
                # Build log entry
                entry = {"node": node_name, "status": "completed"}
                if state_update.get("plan"):
                    entry["plan"] = state_update["plan"]
                if state_update.get("error"):
                    entry["error"] = state_update["error"][:500]
                if state_update.get("code_output"):
                    entry["output"] = state_update["code_output"][:1000]
                if state_update.get("python_code"):
                    entry["code_length"] = len(state_update["python_code"])
                node_log.append(entry)
        
        # Collect charts
        charts = sorted(glob.glob("output*.png"))
        chart_urls = [f"/api/charts/{os.path.basename(c)}" for c in charts]
        
        return {
            "success": True,
            "insight": final_state.get("final_answer", ""),
            "charts": chart_urls,
            "code": final_state.get("python_code", ""),
            "code_output": final_state.get("code_output", ""),
            "error": final_state.get("error"),
            "plan": final_state.get("plan", []),
            "node_log": node_log
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINT: Serve Charts
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@api.get("/api/charts/{filename}")
async def get_chart(filename: str):
    """Serve a generated chart image."""
    filepath = os.path.join(CHART_DIR, filename)
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type="image/png")
    return JSONResponse(
        status_code=404,
        content={"error": f"Chart not found: {filename}"}
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINT: Health Check
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@api.get("/api/health")
async def health():
    return {"status": "ok", "agent": "Auto-Analyst AI"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    print("\n🚀 Auto-Analyst AI — API Server")
    print("   Docs:  http://localhost:8000/docs")
    print("   API:   http://localhost:8000/api\n")
    uvicorn.run(api, host="0.0.0.0", port=8000)
