from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Settings
import chromadb
from dotenv import load_dotenv
import os
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
GOOGLE_API_KEY=os.environ["GOOGLE_API_KEY"]

    
Settings.llm = GoogleGenAI(model="models/gemini-2.5-flash", temperature=0.1)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/embedding-001")

# 1️⃣ Reconnect to your persistent Chroma store
chroma_client = chromadb.PersistentClient("./chroma_store")

# 2️⃣ Get the existing collection
chroma_collection = chroma_client.get_or_create_collection("icd10cm")

# 3️⃣ Rebuild the vector store wrapper
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# 4️⃣ Recreate the storage context
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 5️⃣ Load your index from that storage context
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context
)

print("✅ Index reloaded successfully — ready for querying!")

query_engine = index.as_query_engine()
response = query_engine.query("What is the ICD-10 code for Cholera?")
print(response)