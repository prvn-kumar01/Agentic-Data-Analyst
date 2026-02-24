import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEndpointEmbeddings


load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise ValueError("❌ ERROR: GROQ_API_KEY is missing in .env file!")

if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
    raise ValueError("❌ ERROR: HUGGINGFACEHUB_API_TOKEN is missing in .env file!")


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


embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
)

# Export
__all__ = ["llm_brain", "llm_coder", "embeddings"]