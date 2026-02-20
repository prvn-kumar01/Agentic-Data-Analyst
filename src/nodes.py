"""
Agent Nodes — The Workers of the Auto-Analyst AI Pipeline.
Each node performs a specific task in the analysis workflow:
  1. Profiler  — Loads and summarizes the CSV dataset
  2. Planner   — Creates a step-by-step analysis plan
  3. Generator — Writes Python code to execute the plan
  4. Executor  — Runs the code in a sandbox
  5. Insight   — Summarizes results for the user
"""

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from config import llm_brain, llm_coder
from src.state import AgentState
from src.schema import AnalysisPlan, PythonCode
from src.utils import get_csv_summary
from src.tools import execute_python_code
from src.prompts import PLANNER_PROMPT, CODER_PROMPT, INSIGHT_PROMPT


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NODE 1: PROFILER — Reads & Summarizes CSV
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def profiler_node(state: AgentState):
    print("\n--- 1. 🕵️ PROFILING DATA ---")
    file_path = state["csv_file_path"]
    
    profile = get_csv_summary(file_path)
    
    if not profile.get("success"):
        print(f"❌ Error loading CSV: {profile.get('error')}")
        return {
            "error": f"Failed to load CSV: {profile.get('error')}",
            "dataset_summary": "Error loading data.",
            "columns": []
        }
    
    print(f"✅ Dataset loaded: {len(profile['columns'])} columns")
    return {
        "dataset_summary": profile["text"],
        "columns": profile["columns"],
        "messages": [SystemMessage(content="Data Profiled Successfully.")]
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NODE 2: PLANNER — Creates Analysis Strategy
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def planner_node(state: AgentState):
    print("\n--- 2. 🧠 PLANNING ANALYSIS ---")
    
    parser = JsonOutputParser(pydantic_object=AnalysisPlan)
    
    prompt = PromptTemplate(
        template=PLANNER_PROMPT,
        input_variables=["data_summary", "user_query"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm_brain | parser
    
    try:
        plan_result = chain.invoke({
            "data_summary": state["dataset_summary"],
            "user_query": state["user_query"]
        })
        
        print(f"📋 Plan Generated: {len(plan_result['steps'])} Steps")
        for i, step in enumerate(plan_result['steps']):
            print(f"   {i+1}. {step}")
            
        return {"plan": plan_result['steps']}
        
    except Exception as e:
        print(f"⚠️ Planning Error: {e}")
        return {"plan": ["Load Data", "Analyze based on query", "Plot results"]}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NODE 3: GENERATOR — Writes Python Code
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def generator_node(state: AgentState):
    print("\n--- 3. ⌨️ GENERATING CODE ---")
    
    parser = JsonOutputParser(pydantic_object=PythonCode)
    
    # Prepare Error Context (agar retry ho raha hai)
    error_context = "NO PREVIOUS ERRORS"
    if state.get("error"):
        error_context = f"""
        ⚠️ PREVIOUS CODE FAILED!
        Error Message: {state['error']}
        
        Reflect on this error. You MUST fix the code logic to handle this error.
        Common fixes: check column names, handle NaN, use correct dtypes.
        """

    prompt = PromptTemplate(
        template=CODER_PROMPT,
        input_variables=["data_summary", "plan", "csv_path", "error_context"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm_coder | parser
    
    try:
        code_result = chain.invoke({
            "data_summary": state["dataset_summary"],
            "plan": "\n".join(state["plan"]),
            "csv_path": state["csv_file_path"],
            "error_context": error_context 
        })
        
        print(f"💡 Thought: {code_result['thought_process']}")
        print(f"💻 Code Generated ({len(code_result['code'])} chars)")
        
        return {
            "python_code": code_result['code'],
            "revision_count": state.get("revision_count", 0) + 1,
            "error": None
        }
        
    except Exception as e:
        print(f"❌ Code Generation Failed: {e}")
        return {"error": f"Code Generation Failed: {str(e)}"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NODE 4: EXECUTOR — Runs Code in Sandbox
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def executor_node(state: AgentState):
    print("\n--- 4. ⚙️ EXECUTING CODE ---")
    
    code = state.get("python_code")
    
    if not code:
        print("⚠️ No code to execute. Skipping.")
        return {
            "error": "Execution skipped because no code was generated.",
            "code_output": None
        }
    
    csv_path = state["csv_file_path"]
    
    result = execute_python_code(code, csv_path)
    
    if result["success"]:
        print(f"✅ Execution Success!\nOutput: {result['output']}")
        return {
            "code_output": result["output"],
            "image_path": result.get("image_path", "output.png"),
            "error": None
        }
    else:
        print(f"❌ Execution Failed!\nError: {result['error']}")
        return {
            "code_output": None,
            "error": result["error"]
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NODE 5: INSIGHT — Summarizes Results
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def insight_node(state: AgentState):
    print("\n--- 5. 📊 GENERATING INSIGHTS ---")
    
    query = state["user_query"]
    code_output = state.get("code_output", "No textual output")
    
    prompt = INSIGHT_PROMPT.format(
        query=query,
        code_output=code_output
    )
    
    response = llm_brain.invoke([HumanMessage(content=prompt)])
    final_answer = response.content
    
    print(f"📝 Final Insight: {final_answer[:200]}...")
    
    return {
        "final_answer": final_answer,
        "messages": [SystemMessage(content=final_answer)]
    }