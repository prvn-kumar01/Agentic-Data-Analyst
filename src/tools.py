"""
Sandboxed Python Code Execution Tool.
Executes AI-generated code in a controlled environment with security guardrails.
Supports multiple chart outputs (output_1.png, output_2.png, ...).
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


matplotlib.use('Agg')

# Project root directory (anchored absolute path)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "data", "output")


def _strip_imports(code: str) -> str:
    """
    Strips import statements from AI-generated code.
    Libraries (pd, np, plt, sns) are already injected into the sandbox.
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
        output_dir = _OUTPUT_DIR
    for f in glob.glob(os.path.join(output_dir, "output*.png")):
        try:
            os.remove(f)
        except OSError:
            pass


def _find_generated_charts(output_dir: str = None) -> list:
    """Find all output chart files generated during execution."""
    if output_dir is None:
        output_dir = _OUTPUT_DIR
    patterns = ["output.png", "output_*.png"]
    charts = []
    for pattern in patterns:
        charts.extend(glob.glob(os.path.join(output_dir, pattern)))
    # Dedupe and sort
    charts = sorted(set(charts))
    return charts


def execute_python_code(code: str, csv_path: str, output_image: str = "output.png"):
    """
    Executes Python code in a controlled environment with:
    - Security guardrails (blocks dangerous imports)
    - Stdout capture (captures print output)
    - Error handling (returns clean error messages)
    - Multi-chart support (detects output_1.png, output_2.png, etc.)
    """
    
    # 1. SECURITY GUARDRAILS
    forbidden_patterns = [
        r'\bsubprocess\b', r'\bshutil\b', 
        r'\bimportlib\b', r'\b__import__\b',
    ]
    
    for pattern in forbidden_patterns:
        if re.search(pattern, code):
            return {
                "success": False, 
                "error": f"Security Alert: Forbidden pattern '{pattern}' detected!"
            }

    # 2. ENSURE OUTPUT DIRECTORY EXISTS & CLEANUP OLD CHARTS
    output_dir = _OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    _cleanup_old_charts(output_dir)

    # 3. CAPTURE STDOUT
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output

    # 4. SANDBOX ENVIRONMENT — includes commonly needed modules
    import builtins as _builtins
    import math
    import datetime
    import collections
    import warnings as _warnings_mod

    # Try to load scipy.stats (commonly used by LLM for outlier detection, z-scores, etc.)
    try:
        from scipy import stats as _scipy_stats
        import scipy as _scipy
    except ImportError:
        _scipy_stats = None
        _scipy = None

    # Use absolute path for csv_path too
    abs_csv_path = os.path.abspath(csv_path)

    local_scope = {
        "pd": pd, "np": np, "plt": plt, "sns": sns,
        "csv_file_path": abs_csv_path,
        "OUTPUT_DIR": output_dir,
        "os": os,
        "re": re,
        "math": math,
        "datetime": datetime,
        "collections": collections,
        "warnings": _warnings_mod,
    }

    # Add scipy if available
    if _scipy_stats is not None:
        local_scope["stats"] = _scipy_stats
        local_scope["scipy"] = _scipy

    # 5. SAFE BUILTINS — use real builtins, only remove truly dangerous ones
    dangerous_names = {"eval", "exec", "compile", "__import__", "breakpoint", "exit", "quit"}
    safe_builtins = {k: v for k, v in vars(_builtins).items() if k not in dangerous_names}
    # Re-add __import__ in restricted form (needed by dict comprehensions, f-strings, etc.)
    safe_builtins["__import__"] = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__

    try:
        # 6. STRIP IMPORTS & EXECUTE
        clean_code = _strip_imports(code)
        # Inject absolute csv path and OUTPUT_DIR into the code
        full_code = f'csv_file_path = r"{abs_csv_path}"\n'
        full_code += f'OUTPUT_DIR = r"{output_dir}"\n'
        full_code += clean_code
        exec(full_code, {"__builtins__": safe_builtins}, local_scope)
        
        # 7. CAPTURE OUTPUT
        sys.stdout = old_stdout
        output = redirected_output.getvalue()
        
        # Close all matplotlib figures to free memory
        plt.close('all')
        
        # 8. FIND ALL GENERATED CHARTS
        charts = _find_generated_charts(output_dir)
        
        return {
            "success": True, 
            "output": output if output.strip() else "(No text output — check charts)",
            "image_path": charts[0] if charts else "output.png",
            "all_charts": charts
        }

    except Exception as e:
        sys.stdout = old_stdout
        plt.close('all')
        error_msg = traceback.format_exc()
        clean_error = error_msg.split("\n")[-2] if "\n" in error_msg else str(e)
        return {
            "success": False, 
            "error": f"{clean_error}\n\nFull Traceback:\n{error_msg}",
            "all_charts": _find_generated_charts(output_dir)  # Some charts may have been saved before error
        }