from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes import profiler_node, planner_node, generator_node, executor_node, insight_node



def should_proceed_after_profiling(state: AgentState):
    """If CSV loading failed, skip to END instead of planning with bad data."""
    if state.get("error"):
        print("🛑 Data loading failed. Aborting pipeline.")
        return "abort"
    return "continue"



def should_continue(state: AgentState):
    """
    Decides whether to retry code generation or finish.
    Max 3 retries to prevent infinite loops.
    """
    if not state.get("error"):
        return "end"
    
    retry_count = state.get("revision_count", 0)
    
    if retry_count < 3:
        print(f"🔄 Retrying... (Attempt {retry_count + 1}/3)")
        return "retry"
    
    print("🛑 Max retries reached. Proceeding with available results.")
    return "end"



workflow = StateGraph(AgentState)


workflow.add_node("profiler", profiler_node)
workflow.add_node("planner", planner_node)
workflow.add_node("generator", generator_node)
workflow.add_node("executor", executor_node)
workflow.add_node("insight", insight_node)

# Entry Point
workflow.set_entry_point("profiler")

# Profiler → Check if data loaded successfully
workflow.add_conditional_edges(
    "profiler",
    should_proceed_after_profiling,
    {
        "continue": "planner",
        "abort": END
    }
)

# Linear Flow: planner → generator → executor
workflow.add_edge("planner", "generator")
workflow.add_edge("generator", "executor")

# Conditional: executor → retry (generator) OR finish (insight)
workflow.add_conditional_edges(
    "executor",
    should_continue,
    {
        "retry": "generator",
        "end": "insight" 
    }
)

# Final → END
workflow.add_edge("insight", END) 

# Compile
app = workflow.compile()