from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from dotenv import load_dotenv
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
import chromadb
import os
import asyncio

load_dotenv()

Settings.llm = GoogleGenAI(model="models/gemini-2.5-flash", temperature=0.1)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/embedding-001")

CHROMA_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "chroma_store"))

chroma_client = chromadb.PersistentClient(CHROMA_DB_PATH)
chroma_collection = chroma_client.get_or_create_collection("icd10cm")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context
)

query_engine = index.as_query_engine()

def search_icd10_code(symptoms: str):
    """
    Receives symptoms and returns the most relevant ICD-10 code.
    """
    response = query_engine.query(symptoms)
    return response
