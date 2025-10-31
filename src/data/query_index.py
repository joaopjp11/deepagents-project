# Script for querying the ICD-10 INDEX vector store
# Uses MiniLM embeddings and Gemini LLM for testing

import chromadb
from dotenv import load_dotenv
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()

# Configuração LLM e Embeddings
Settings.llm = GoogleGenAI(model="models/gemini-2.5-flash", temperature=0.1)
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Inicializa cliente Chroma
chroma_client = chromadb.PersistentClient("./chroma_store")
chroma_collection = chroma_client.get_or_create_collection("icd10_index")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Recarrega o índice a partir do vector store
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context
)

print("✅ ICD-10 INDEX successfully reloaded — ready for querying!")

# Cria motor de query
query_engine = index.as_query_engine()

# Query de exemplo
query = "What is the ICD-10 code for Hereditary lymphedema?"
response = query_engine.query(query)

print("Query:", query)
print("Response:", response)
