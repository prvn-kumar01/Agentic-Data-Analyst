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


def _cleanup_old_charts(output_dir: str = os.path.join("data", "output")):
    """Remove previous output charts before a new run."""
    for f in glob.glob(os.path.join(output_dir, "output*.png")):
        try:
            os.remove(f)
        except OSError:
            pass


def _find_generated_charts(output_dir: str = os.path.join("data", "output")) -> list:
    """Find all output chart files generated during execution."""
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
    output_dir = os.path.join("data", "output")
    os.makedirs(output_dir, exist_ok=True)
    _cleanup_old_charts(output_dir)

    # 3. CAPTURE STDOUT
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output

    # 4. SANDBOX ENVIRONMENT
    local_scope = {
        "pd": pd, "np": np, "plt": plt, "sns": sns,
        "csv_file_path": csv_path
    }

    # 5. SAFE BUILTINS
    safe_builtins = {
        "print": print, "len": len, "range": range, "enumerate": enumerate,
        "zip": zip, "map": map, "filter": filter, "sorted": sorted,
        "reversed": reversed, "list": list, "dict": dict, "set": set,
        "tuple": tuple, "str": str, "int": int, "float": float, "bool": bool,
        "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
        "any": any, "all": all, "isinstance": isinstance, "type": type,
        "hasattr": hasattr, "getattr": getattr, "setattr": setattr,
        "ValueError": ValueError, "TypeError": TypeError, "KeyError": KeyError,
        "IndexError": IndexError, "Exception": Exception,
        "True": True, "False": False, "None": None,
    }

    try:
        # 6. STRIP IMPORTS & EXECUTE
        clean_code = _strip_imports(code)
        full_code = f'csv_file_path = r"{csv_path}"\n' + clean_code
        exec(full_code, {"__builtins__": safe_builtins}, local_scope)
        
        # 7. CAPTURE OUTPUT
        sys.stdout = old_stdout
        output = redirected_output.getvalue()
        
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
        error_msg = traceback.format_exc()
        clean_error = error_msg.split("\n")[-2] if "\n" in error_msg else str(e)
        return {
            "success": False, 
            "error": f"{clean_error}\n\nFull Traceback:\n{error_msg}",
            "all_charts": _find_generated_charts(output_dir)  # Some charts may have been saved before error
        }