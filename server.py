import os
import sys
import glob
import shutil
import uuid
import zipfile
import asyncio
import logging
import pandas as pd
from io import StringIO

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.graph import app as agent_app

# Structured Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("auto_analyst.server")

api = FastAPI(
    title="Auto-Analyst AI",
    description="Autonomous Data Analysis Agent API — Production Ready",
    version="2.0.0"
)

# CORS — Allow Streamlit & Production Frontends
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories (use absolute paths based on script location)
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(_PROJECT_ROOT, "data", "input")
CHART_DIR = os.path.join(_PROJECT_ROOT, "data", "output")  
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)


@api.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a CSV/Excel/JSON file, convert to CSV if needed, and return a data preview."""
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        
        try:
            if ext in ("xlsx", "xls"):
                df = pd.read_excel(file_path)
            elif ext == "json":
                df = pd.read_json(file_path)
            else:
                df = pd.read_csv(file_path)
        except Exception as read_err:
            logger.error(f"Failed to read uploaded file: {read_err}")
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": f"Cannot read file: {read_err}"}
            )
        
        if ext in ("xlsx", "xls", "json"):
            csv_filename = file.filename.rsplit(".", 1)[0] + ".csv"
            file_path = os.path.join(UPLOAD_DIR, csv_filename)
            df.to_csv(file_path, index=False)
        
        columns_info = []
        for col in df.columns:
            non_null = int(df[col].notna().sum())
            unique = int(df[col].nunique())
            sample_val = "N/A"
            if not df[col].dropna().empty:
                sample_val = str(df[col].dropna().iloc[0])
            columns_info.append({
                "name": str(col),
                "dtype": str(df[col].dtype),
                "non_null": non_null,
                "unique": unique,
                "sample": sample_val
            })
        
        # Replace NaN with empty string for valid JSON serialization
        preview_records = df.head(8).fillna("").to_dict(orient="records")
        
        return {
            "success": True,
            "filename": os.path.basename(file_path),
            "filepath": file_path,
            "rows": df.shape[0],
            "cols": df.shape[1],
            "columns": columns_info,
            "preview": preview_records,
            "column_names": [str(c) for c in df.columns]
        }
    
    except Exception as e:
        logger.exception("Error in /api/upload endpoint")
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )


@api.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file, extract tables, convert to CSV and return preview."""
    try:
        import pdfplumber

        pdf_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(pdf_path, "wb") as f:
            content = await file.read()
            f.write(content)

        all_tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table and len(table) > 1:
                        header = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(table[0])]
                        rows = table[1:]
                        tdf = pd.DataFrame(rows, columns=header)
                        all_tables.append(tdf)

        if not all_tables:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "No tables found in the PDF. Please upload a PDF with tabular data."}
            )

        df = pd.concat(all_tables, ignore_index=True)
        csv_filename = file.filename.rsplit(".", 1)[0] + ".csv"
        csv_path = os.path.join(UPLOAD_DIR, csv_filename)
        df.to_csv(csv_path, index=False)

        columns_info = []
        for col in df.columns:
            non_null = int(df[col].notna().sum())
            unique = int(df[col].nunique())
            sample_val = "N/A"
            if not df[col].dropna().empty:
                sample_val = str(df[col].dropna().iloc[0])
            columns_info.append({
                "name": str(col),
                "dtype": str(df[col].dtype),
                "non_null": non_null,
                "unique": unique,
                "sample": sample_val
            })

        preview_records = df.head(8).fillna("").to_dict(orient="records")

        return {
            "success": True,
            "filename": csv_filename,
            "filepath": csv_path,
            "original_pdf": file.filename,
            "rows": df.shape[0],
            "cols": df.shape[1],
            "columns": columns_info,
            "preview": preview_records,
            "column_names": [str(c) for c in df.columns]
        }

    except ImportError:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "pdfplumber not installed. Run: pip install pdfplumber"}
        )
    except Exception as e:
        logger.exception("Error in /api/upload-pdf endpoint")
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )


def _run_agent_pipeline_sync(initial_state: dict, thread_id: str):
    """Synchronous worker function to stream the agent pipeline without blocking event loop."""
    final_state = {}
    node_log = []
    
    config = {"configurable": {"thread_id": thread_id}}
    
    for output in agent_app.stream(initial_state, config=config):
        for node_name, state_update in output.items():
            if state_update is None:
                continue
            final_state.update(state_update)
            
            entry = {"node": node_name, "status": "completed"}
            if state_update.get("plan"):
                entry["plan"] = state_update["plan"]
            if state_update.get("error"):
                entry["error"] = str(state_update["error"])[:500]
            if state_update.get("code_output"):
                entry["output"] = str(state_update["code_output"])[:1000]
            if state_update.get("python_code"):
                entry["code_length"] = len(state_update["python_code"])
            node_log.append(entry)

    return final_state, node_log


@api.post("/api/analyze")
async def analyze_data(
    filepath: str = Form(...),
    query: str = Form(...),
    thread_id: str = Form(None)
):
    """Run the full agent pipeline asynchronously in isolated job directory."""
    if not os.path.exists(filepath):
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": f"File not found: {filepath}"}
        )
    
    # Generate unique Job ID for multi-tenant isolation
    job_id = uuid.uuid4().hex[:10]
    if not thread_id:
        thread_id = job_id
        
    job_output_dir = os.path.join(CHART_DIR, job_id)
    os.makedirs(job_output_dir, exist_ok=True)
    
    logger.info(f"Starting Analysis Job '{job_id}' for query: {query}")
    
    initial_state = {
        "csv_file_path": filepath,
        "user_query": query,
        "revision_count": 0,
        "messages": [],
        "job_id": job_id,
        "output_dir": job_output_dir
    }
    
    try:
        # Non-blocking execution via asyncio thread pool
        final_state, node_log = await asyncio.to_thread(_run_agent_pipeline_sync, initial_state, thread_id)
        
        # Collect all charts from session directory (Plotly JSON and Matplotlib PNG)
        json_charts = glob.glob(os.path.join(job_output_dir, "output*.json"))
        png_charts = glob.glob(os.path.join(job_output_dir, "output*.png"))
        html_charts = glob.glob(os.path.join(job_output_dir, "output*.html"))
        charts = sorted(set(json_charts + png_charts + html_charts))
            
        chart_urls = [f"/api/charts/{job_id}/{os.path.basename(c)}" for c in charts]
        
        # Save analysis summary report into job directory for zip export
        report_md = f"# Auto-Analyst AI Summary Report (Job: {job_id})\n\n"
        report_md += f"**User Query:** {query}\n\n"
        report_md += f"## Insights\n{final_state.get('final_answer', '')}\n\n"
        report_md += f"## Execution Output\n```\n{final_state.get('code_output', '')}\n```\n"
        
        with open(os.path.join(job_output_dir, "report.md"), "w", encoding="utf-8") as rf:
            rf.write(report_md)

        if final_state.get("python_code"):
            with open(os.path.join(job_output_dir, "analysis_script.py"), "w", encoding="utf-8") as cf:
                cf.write(final_state["python_code"])
        
        return {
            "success": True,
            "job_id": job_id,
            "insight": final_state.get("final_answer", ""),
            "charts": chart_urls,
            "code": final_state.get("python_code", ""),
            "code_output": final_state.get("code_output", ""),
            "error": final_state.get("error"),
            "plan": final_state.get("plan", []),
            "node_log": node_log
        }
    
    except Exception as e:
        logger.exception(f"Job '{job_id}' encountered error during pipeline execution")
        return JSONResponse(
            status_code=500,
            content={"success": False, "job_id": job_id, "error": str(e)}
        )


@api.get("/api/charts/{job_id}/{filename}")
async def get_job_chart(job_id: str, filename: str):
    """Serve a generated chart from a specific job directory."""
    # Sanitize filenames to prevent directory traversal
    clean_job_id = os.path.basename(job_id)
    clean_filename = os.path.basename(filename)
    filepath = os.path.join(CHART_DIR, clean_job_id, clean_filename)
    
    if os.path.exists(filepath):
        if clean_filename.endswith(".json"):
            return FileResponse(filepath, media_type="application/json")
        elif clean_filename.endswith(".html"):
            return FileResponse(filepath, media_type="text/html")
        elif clean_filename.endswith(".svg"):
            return FileResponse(filepath, media_type="image/svg+xml")
        return FileResponse(filepath, media_type="image/png")
    return JSONResponse(
        status_code=404,
        content={"error": f"Chart not found for job '{clean_job_id}': {clean_filename}"}
    )


@api.get("/api/charts/{filename}")
async def get_legacy_chart(filename: str):
    """Fallback route for legacy chart requests."""
    clean_filename = os.path.basename(filename)
    filepath = os.path.join(CHART_DIR, clean_filename)
    if os.path.exists(filepath):
        if clean_filename.endswith(".json"):
            return FileResponse(filepath, media_type="application/json")
        return FileResponse(filepath, media_type="image/png")
    return JSONResponse(
        status_code=404,
        content={"error": f"Chart not found: {clean_filename}"}
    )


@api.get("/api/download-report/{job_id}")
async def download_report_zip(job_id: str):
    """Package job charts, code, and report into a downloadable ZIP archive."""
    clean_job_id = os.path.basename(job_id)
    job_output_dir = os.path.join(CHART_DIR, clean_job_id)
    if not os.path.exists(job_output_dir):
        return JSONResponse(
            status_code=404,
            content={"error": f"Job directory for '{clean_job_id}' not found."}
        )

    zip_filename = f"AutoAnalyst_Report_{clean_job_id}.zip"
    zip_path = os.path.join(CHART_DIR, zip_filename)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(job_output_dir):
            for file in files:
                if file.endswith(".zip"):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, job_output_dir)
                zipf.write(file_path, arcname)

    return FileResponse(
        path=zip_path,
        filename=zip_filename,
        media_type="application/zip"
    )


@api.get("/api/health")
async def health():
    return {"status": "ok", "agent": "Auto-Analyst AI v2.0", "engine": "FastAPI + LangGraph"}


if __name__ == "__main__":
    logger.info("Starting Auto-Analyst AI Production Server on http://0.0.0.0:8000")
    uvicorn.run(api, host="0.0.0.0", port=8000)
