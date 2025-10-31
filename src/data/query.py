# Script for querying the ICD-10 vector index
# This script reloads the vector index and runs a sample query

import chromadb
from dotenv import load_dotenv
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()

# LLM and embedding model configuration
Settings.llm = GoogleGenAI(model="models/gemini-2.5-flash", temperature=0.1)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/embedding-001")

# Initialize Chroma client
chroma_client = chromadb.PersistentClient("./chroma_store")
chroma_collection = chroma_client.get_or_create_collection("icd10cm")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Reload the vector index from the vector store
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context
)

print("✅ Index successfully reloaded — ready for querying!")

query_engine = index.as_query_engine()

# Example query
response = query_engine.query("What is the ICD-10 code for Hereditary lymphedema?")
print(response)