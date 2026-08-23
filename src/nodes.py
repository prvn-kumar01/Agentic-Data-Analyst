import re
import sys
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from config import llm_brain, llm_coder
from src.state import AgentState
from src.schema import AnalysisPlan, PythonCode
from src.utils import get_csv_summary
from src.tools import execute_python_code
from src.prompts import PLANNER_PROMPT, CODER_PROMPT, INSIGHT_PROMPT

# Configure stdout for safe UTF-8 printing on Windows
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _safe_print(*args, **kwargs):
    """Print safely without crashing on Windows console charmap encoding limitations."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or 'utf-8'
        cleaned = [str(a).encode(encoding, errors='replace').decode(encoding) for a in args]
        try:
            print(*cleaned, **kwargs)
        except Exception:
            pass
    except Exception:
        pass


def _extract_code_from_text(text: str) -> str:
    """Fallback extraction of Python code from markdown blocks or raw text."""
    match = re.search(r'```(?:python)?\s*\n(.*?)```', text, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def profiler_node(state: AgentState):
    _safe_print("\n--- 1. PROFILING DATA ---")
    file_path = state["csv_file_path"]
    
    profile = get_csv_summary(file_path)
    
    if not profile.get("success"):
        _safe_print(f"[ERROR] Error loading CSV: {profile.get('error')}")
        return {
            "error": f"Failed to load CSV: {profile.get('error')}",
            "dataset_summary": "Error loading data.",
            "columns": [],
            "python_code": None,
            "code_output": None
        }
    
    _safe_print(f"[OK] Dataset loaded: {len(profile['columns'])} columns")
    return {
        "dataset_summary": profile["text"],
        "columns": profile["columns"],
        "error": None,
        "python_code": None,
        "code_output": None,
        "messages": [SystemMessage(content="Data Profiled Successfully.")]
    }


def planner_node(state: AgentState):
    _safe_print("\n--- 2. PLANNING ANALYSIS ---")
    
    parser = JsonOutputParser(pydantic_object=AnalysisPlan)
    
    prompt = PromptTemplate(
        template=PLANNER_PROMPT,
        input_variables=["data_summary", "user_query"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm_brain
    
    try:
        raw_response = chain.invoke({
            "data_summary": state["dataset_summary"],
            "user_query": state["user_query"]
        })
        
        content = raw_response.content if hasattr(raw_response, 'content') else str(raw_response)
        try:
            plan_result = parser.parse(content)
            steps = plan_result.get('steps', [])
        except Exception:
            steps = [line.strip().lstrip('0123456789.-* ') for line in content.split('\n') if line.strip() and ('1.' in line or '2.' in line or '3.' in line or '-' in line)]
            if not steps:
                steps = ["Load Data", "Analyze distributions & summaries", "Plot interactive charts"]
        
        _safe_print(f"[PLAN] Plan Generated: {len(steps)} Steps")
        for i, step in enumerate(steps):
            _safe_print(f"   {i+1}. {step}")
            
        return {
            "plan": steps,
            "error": None
        }
        
    except Exception as e:
        _safe_print(f"[WARN] Planning Error: {e}")
        return {
            "plan": ["Load Data", "Analyze based on query", "Plot results"],
            "error": None
        }


def generator_node(state: AgentState):
    _safe_print("\n--- 3. GENERATING CODE ---")
    
    parser = JsonOutputParser(pydantic_object=PythonCode)
    
    error_context = "NO PREVIOUS ERRORS"
    if state.get("error"):
        error_context = f"""
        [WARNING] PREVIOUS CODE FAILED!
        Error Message: {state['error']}
        
        Reflect on this error. You MUST fix the code logic to handle this error.
        Common fixes: check column names, handle NaN, use correct dtypes.
        """

    prompt = PromptTemplate(
        template=CODER_PROMPT,
        input_variables=["data_summary", "plan", "error_context"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm_coder
    
    plan = state.get("plan", ["Load Data", "Analyze based on query", "Plot results"])
    if isinstance(plan, str):
        plan = [plan]
    
    try:
        raw_response = chain.invoke({
            "data_summary": state.get("dataset_summary", "No summary available"),
            "plan": "\n".join(plan),
            "error_context": error_context 
        })
        
        content = raw_response.content if hasattr(raw_response, 'content') else str(raw_response)
        
        code = None
        thought = "Generated Python analysis script"
        try:
            code_result = parser.parse(content)
            code = code_result.get('code')
            thought = code_result.get('thought_process', thought)
        except Exception:
            code = _extract_code_from_text(content)
        
        if not code:
            raise ValueError("No executable code could be extracted from model output.")
        
        _safe_print(f"[THOUGHT] {thought[:100]}...")
        _safe_print(f"[CODE] Code Generated ({len(code)} chars)")
        
        return {
            "python_code": code,
            "revision_count": state.get("revision_count", 0) + 1,
            "error": None
        }
        
    except Exception as e:
        _safe_print(f"[ERROR] Code Generation Failed: {e}")
        return {
            "error": f"Code Generation Failed: {str(e)}",
            "revision_count": state.get("revision_count", 0) + 1
        }


def executor_node(state: AgentState):
    _safe_print("\n--- 4. EXECUTING CODE ---")
    
    code = state.get("python_code")
    
    if not code:
        _safe_print("[WARN] No code to execute. Skipping.")
        return {
            "error": "Execution skipped because no code was generated.",
            "code_output": None
        }
    
    csv_path = state["csv_file_path"]
    output_dir = state.get("output_dir")
    
    result = execute_python_code(code, csv_path, output_dir=output_dir)
    
    if result["success"]:
        _safe_print(f"[OK] Execution Success!\nOutput: {result['output'][:200]}...")
        return {
            "code_output": result["output"],
            "image_path": result.get("image_path", "output.png"),
            "error": None
        }
    else:
        _safe_print(f"[ERROR] Execution Failed!\nError: {result['error']}")
        return {
            "code_output": None,
            "error": result["error"]
        }


def insight_node(state: AgentState):
    _safe_print("\n--- 5. GENERATING INSIGHTS ---")
    
    query = state.get("user_query", "Analyze the data")
    code_output = state.get("code_output") or "No textual output available"
    error = state.get("error")
    
    if error and code_output == "No textual output available":
        code_output = f"Code execution encountered an error: {error}\nPlease summarize what went wrong and suggest next steps."
    
    try:
        prompt = INSIGHT_PROMPT.replace("{query}", str(query)).replace("{code_output}", str(code_output))
        
        response = llm_brain.invoke([HumanMessage(content=prompt)])
        final_answer = response.content
        
        _safe_print(f"[INSIGHT] Final Insight: {final_answer[:200]}...")
        
        return {
            "final_answer": final_answer,
            "messages": [SystemMessage(content=final_answer)]
        }
    except Exception as e:
        _safe_print(f"[ERROR] Insight generation failed: {e}")
        fallback = f"Analysis completed but insight generation encountered an error: {str(e)}\n\nRaw output from analysis:\n{str(code_output)[:500]}"
        return {
            "final_answer": fallback,
            "messages": [SystemMessage(content=fallback)]
        }