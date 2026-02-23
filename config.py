import os
import torch
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings


load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise ValueError("❌ ERROR: GROQ_API_KEY is missing in .env file!")


llm_brain = ChatGroq(
    model_name="llama-3.3-70b-versatile", 
    temperature=0.2, 
    max_retries=2
)


llm_coder = ChatGroq(
    model_name="llama-3.3-70b-versatile", 
    temperature=0,   
    max_retries=2
)


device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 System Hardware: Embeddings running on {device.upper()}")

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': device}
)

# Export
__all__ = ["llm_brain", "llm_coder", "embeddings"]