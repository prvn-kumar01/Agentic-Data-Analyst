from typing import TypedDict, Annotated, List, Union, Optional
import operator
from langchain_core.messages import AnyMessage

class AgentState(TypedDict):
    # 1. Inputs
    csv_file_path: str
    user_query: str
    
    # 2. Data Understanding
    dataset_summary: str
    columns: List[str]
    
    # 3. Planning
    plan: List[str]
    
    # 4. Execution Memory
    python_code: Optional[str] 
    code_output: Optional[str]
    error: Optional[str]
    image_path: Optional[str]
    
    # 5. Final Output
    final_answer: Optional[str]
    
    # 6. Conversation History
    messages: Annotated[List[AnyMessage], operator.add]
    
    # 7. Safety & Loops
    revision_count: int