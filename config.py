import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise ValueError("❌ ERROR: GROQ_API_KEY is missing in .env file!")

if not os.getenv("E2B_API_KEY"):
    raise ValueError("❌ ERROR: E2B_API_KEY is missing in .env file!")

# Best model from Groq Console (GPT OSS 120B)
model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

llm_brain = ChatGroq(
    model=model_name, 
    temperature=0.2, 
    max_retries=3,
    request_timeout=90
)

llm_coder = ChatGroq(
    model=model_name, 
    temperature=0.1,   
    max_retries=3,
    request_timeout=90
)

# Optional HuggingFace Embeddings (lazy loaded only on demand)
embeddings = None

def get_embeddings():
    global embeddings
    if embeddings is None and os.getenv("HUGGINGFACEHUB_API_TOKEN"):
        try:
            from langchain_huggingface import HuggingFaceEndpointEmbeddings
            embeddings = HuggingFaceEndpointEmbeddings(
                model="sentence-transformers/all-MiniLM-L6-v2",
                huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            )
        except Exception:
            embeddings = None
    return embeddings

# Export
__all__ = ["llm_brain", "llm_coder", "model_name", "embeddings", "get_embeddings"]