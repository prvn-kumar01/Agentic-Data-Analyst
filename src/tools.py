"""
Sandboxed Python Code Execution Tool.
Executes AI-generated code in an isolated process with security guardrails and execution timeouts.
Supports session-specific chart output directories and multi-chart outputs.
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

logger = logging.getLogger("auto_analyst.tools")
matplotlib.use('Agg')

# Project root directory (anchored absolute path)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "data", "output")


def _strip_imports(code: str) -> str:
    """
    Strips import statements from AI-generated code.
    Libraries (pd, np, plt, sns) are injected into the sandbox.
    """
    lines = code.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from '):
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)


def _cleanup_old_charts(output_dir: str = None):
    """Remove previous output charts before a new run."""
    if output_dir is None:
        output_dir = _DEFAULT_OUTPUT_DIR
    if os.path.exists(output_dir):
        for f in glob.glob(os.path.join(output_dir, "output*.png")):
            try:
                os.remove(f)
            except OSError:
                pass


def _find_generated_charts(output_dir: str = None) -> list:
    """Find all output chart files generated during execution."""
    if output_dir is None:
        output_dir = _DEFAULT_OUTPUT_DIR
    if not os.path.exists(output_dir):
        return []
    patterns = ["output.png", "output_*.png"]
    charts = []
    for pattern in patterns:
        charts.extend(glob.glob(os.path.join(output_dir, pattern)))
    # Dedupe and sort
    charts = sorted(set(charts))
    return charts


def execute_python_code(code: str, csv_path: str, output_dir: str = None, timeout: int = 30):
    """
    Executes Python code in an isolated process with:
    - Security guardrails (blocks dangerous patterns)
    - Subprocess isolation & 30s Execution Timeout
    - Dynamic Session Output Directory support
    - Multi-chart capture
    """
    if output_dir is None:
        output_dir = _DEFAULT_OUTPUT_DIR
    
    os.makedirs(output_dir, exist_ok=True)
    _cleanup_old_charts(output_dir)

    # 1. SECURITY GUARDRAILS
    forbidden_patterns = [
        r'\bsubprocess\b', r'\bshutil\b', 
        r'\bimportlib\b', r'\b__import__\b',
        r'\bos\.system\b', r'\bos\.popen\b',
    ]
    
    for pattern in forbidden_patterns:
        if re.search(pattern, code):
            logger.warning(f"Forbidden pattern '{pattern}' detected in generated code!")
            return {
                "success": False, 
                "error": f"Security Alert: Forbidden pattern '{pattern}' detected in generated code!"
            }

    abs_csv_path = os.path.abspath(csv_path)
    abs_output_dir = os.path.abspath(output_dir)

    # Prepare script content for isolated subprocess execution
    clean_code = _strip_imports(code)
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

try:
    from scipy import stats
    import scipy
except ImportError:
    stats = None
    scipy = None

csv_file_path = r"{abs_csv_path}"
OUTPUT_DIR = r"{abs_output_dir}"

# User Code Execution
{clean_code}
'''

    script_path = os.path.join(abs_output_dir, "_runner_temp.py")
    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        # Execute in isolated subprocess with timeout
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=abs_output_dir
        )

        stdout = result.stdout
        stderr = result.stderr

        # Clean up temporary script
        if os.path.exists(script_path):
            os.remove(script_path)

        charts = _find_generated_charts(abs_output_dir)

        if result.returncode == 0:
            return {
                "success": True,
                "output": stdout.strip() if stdout.strip() else "(No text output — check charts)",
                "image_path": charts[0] if charts else "output.png",
                "all_charts": charts
            }
        else:
            clean_error = stderr.strip().split("\n")[-1] if stderr.strip() else "Unknown Execution Error"
            return {
                "success": False,
                "error": f"{clean_error}\n\nFull Error Log:\n{stderr.strip()}",
                "all_charts": charts
            }

    except subprocess.TimeoutExpired:
        if os.path.exists(script_path):
            try:
                os.remove(script_path)
            except OSError:
                pass
        return {
            "success": False,
            "error": f"Execution Timed Out! The code took longer than {timeout} seconds to execute.",
            "all_charts": _find_generated_charts(abs_output_dir)
        }
    except Exception as e:
        if os.path.exists(script_path):
            try:
                os.remove(script_path)
            except OSError:
                pass
        return {
            "success": False,
            "error": f"Execution Failed: {str(e)}",
            "all_charts": _find_generated_charts(abs_output_dir)
        }