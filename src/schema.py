from pydantic import BaseModel, Field
from typing import List


class AnalysisPlan(BaseModel):
    steps: List[str] = Field(
        description="A list of logical steps to answer the user query. E.g., ['Load data', 'Group by Region', 'Calculate Mean Sales']"
    )
    explanation: str = Field(
        description="A brief explanation of why these steps were chosen."
    )


class PythonCode(BaseModel):
    thought_process: str = Field(
        description="Your internal reasoning before writing code. Why are you choosing this logic?"
    )
    code: str = Field(
        description="Valid Python code using Pandas/Matplotlib. No markdown backticks."
    )
    libraries: List[str] = Field(
        description="List of libraries imported (e.g., ['pandas', 'matplotlib'])."
    )