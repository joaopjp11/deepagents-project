import os
import chromadb
from dotenv import load_dotenv
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()

CHROMA_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "chroma_store"))

# Configuration LLM and Embeddings
Settings.llm = GoogleGenAI(model="models/gemini-2.5-flash", temperature=0.1)
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize Chroma client
chroma_client = chromadb.PersistentClient(CHROMA_DB_PATH)
chroma_collection = chroma_client.get_or_create_collection("icd10_index")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Reload the index from the vector store
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context
)

query_engine = index.as_query_engine()

def search_icd10_code_index(symptoms: str):
    """
    Receives symptoms and returns the most relevant ICD-10 code.
    Uses Index data.
    """
    response = query_engine.query(symptoms)

    sources = response.source_nodes
    icd10_codes = []
    confidences = []
    notes_list = []

    for i in sources:
        code = i.metadata.get("code", "Unknown")
        confidence = round(i.score, 3)
        note = f"Match: {code}. Based on similarity of symptoms to ICD-10 descriptions."

        icd10_codes.append(code)
        confidences.append(confidence)
        notes_list.append(note)

    return {
        "icd10_codes": icd10_codes,
        "confidence": confidences,
        "notes": notes_list
    }
