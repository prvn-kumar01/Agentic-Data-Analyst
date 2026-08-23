"""
Sandboxed Python Code Execution Tool using E2B.
Executes AI-generated code in an isolated cloud process with security guardrails and execution timeouts.
Supports session-specific chart output directories and multi-chart outputs (Plotly JSON).
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import io
import sys
import os
import re
import glob
import traceback
import subprocess
import logging
from e2b_code_interpreter import Sandbox

logger = logging.getLogger("auto_analyst.tools")
matplotlib.use('Agg')

# Project root directory (anchored absolute path)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "data", "output")


def _natural_sort_key(s: str):
    """Sort strings with embedded numbers naturally (e.g. output_2 before output_10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]


def _strip_imports(code: str) -> str:
    """
    Cleans up any potential interactive display calls that fail in headless sandbox.
    Keeps imports intact to avoid indentation or module resolution errors.
    """
    # Disable any interactive show calls (e.g. plt.show(), fig.show(), fig1.show(), etc.)
    cleaned = re.sub(r'^\s*(?:plt|\w+)\.show\(.*?\)', '# show() suppressed in headless sandbox', code, flags=re.MULTILINE)
    return cleaned


def _cleanup_old_charts(output_dir: str = None):
    """Remove previous output charts before a new run."""
    if output_dir is None:
        output_dir = _DEFAULT_OUTPUT_DIR
    if os.path.exists(output_dir):
        patterns = ["*.png", "*.json", "*.html", "*.svg", "*.jpg", "*.jpeg"]
        for pattern in patterns:
            for f in glob.glob(os.path.join(output_dir, pattern)):
                try:
                    os.remove(f)
                except OSError:
                    pass


def _find_generated_charts(output_dir: str = None) -> list:
    """Find all output chart files generated during execution with natural ordering."""
    if output_dir is None:
        output_dir = _DEFAULT_OUTPUT_DIR
    if not os.path.exists(output_dir):
        return []
    
    valid_exts = {".png", ".json", ".html", ".svg", ".jpg", ".jpeg"}
    charts = []
    for f in os.listdir(output_dir):
        full_path = os.path.join(output_dir, f)
        if os.path.isfile(full_path):
            _, ext = os.path.splitext(f)
            if ext.lower() in valid_exts and not f.startswith("report"):
                charts.append(full_path)
                
    # Dedupe and natural sort
    charts = sorted(set(charts), key=_natural_sort_key)
    return charts


def execute_python_code(code: str, csv_path: str, output_dir: str = None, timeout: int = 60):
    """
    Executes Python code using E2B Sandbox:
    - Secure Cloud Sandbox Isolation
    - Dynamic Session Output Directory support
    - Multi-chart capture (Plotly & Matplotlib)
    """
    if output_dir is None:
        output_dir = _DEFAULT_OUTPUT_DIR
    
    os.makedirs(output_dir, exist_ok=True)
    _cleanup_old_charts(output_dir)

    abs_csv_path = os.path.abspath(csv_path)
    abs_output_dir = os.path.abspath(output_dir)

    clean_code = _strip_imports(code)
    
    # E2B Sandbox paths (using /tmp/data which is user-writable in E2B Linux environment)
    filename = os.path.basename(abs_csv_path)
    sandbox_csv_path = f"/tmp/data/{filename}"
    sandbox_output_dir = f"/tmp/data/output"
    
    # Prepare script content
    script_content = f'''import sys
import os
import re
import math
import datetime
import collections
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

try:
    import polars as pl
except ImportError:
    pl = None

try:
    from scipy import stats
    import scipy
except ImportError:
    stats = None
    scipy = None

csv_file_path = r"{sandbox_csv_path}"
OUTPUT_DIR = r"{sandbox_output_dir}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# User Code Execution
{clean_code}
'''

    try:
        api_key = os.getenv("E2B_API_KEY")
        # Initialize E2B Sandbox using modern E2B v2 create method
        with Sandbox.create(api_key=api_key) as sandbox:
            # Ensure sandbox directory exists
            sandbox.commands.run(f"mkdir -p {sandbox_output_dir}")
            
            # Upload CSV with binary content
            with open(abs_csv_path, "rb") as f:
                sandbox.files.write(sandbox_csv_path, f.read())
            
            # Execute code
            execution = sandbox.run_code(script_content, timeout=timeout)
            
            # Fetch generated files from sandbox
            try:
                entries = sandbox.files.list(sandbox_output_dir)
                for entry in entries:
                    is_dir = getattr(entry, 'is_dir', False) or getattr(entry, 'type', '') == 'dir'
                    if is_dir or not getattr(entry, 'name', None):
                        continue
                    
                    entry_path = getattr(entry, 'path', f"{sandbox_output_dir}/{entry.name}")
                    try:
                        file_data = sandbox.files.read(entry_path)
                        target_local_path = os.path.join(abs_output_dir, entry.name)
                        if isinstance(file_data, bytes):
                            with open(target_local_path, "wb") as f:
                                f.write(file_data)
                        else:
                            with open(target_local_path, "w", encoding="utf-8") as f:
                                f.write(str(file_data))
                    except Exception as read_e:
                        logger.warning(f"Could not download {entry.name} from sandbox: {read_e}")
            except Exception as list_e:
                logger.warning(f"Could not list sandbox output dir: {list_e}")
            
            charts = _find_generated_charts(abs_output_dir)
            
            if execution.error:
                clean_error = execution.error.value
                tb = execution.error.traceback or ""
                return {
                    "success": False,
                    "error": f"{clean_error}\n\nTraceback:\n{tb}",
                    "all_charts": charts
                }
            else:
                stdout_text = ""
                if execution.logs.stdout:
                    stdout_text = "\n".join(execution.logs.stdout)
                
                return {
                    "success": True,
                    "output": stdout_text.strip() if stdout_text.strip() else "(No text output — check charts)",
                    "image_path": charts[0] if charts else "output.json",
                    "all_charts": charts
                }

    except Exception as e:
        return {
            "success": False,
            "error": f"Sandbox Execution Failed: {str(e)}",
            "all_charts": _find_generated_charts(abs_output_dir)
        }