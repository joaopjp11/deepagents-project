# ICD-10 document generator for vector indexing with ICD10-Index data
# This script reads the first N codes from the extracted CSV file, creates Document objects and indexes them in ChromaDB

import pandas as pd
import chromadb
from dotenv import load_dotenv
from llama_index.core import Document, StorageContext, VectorStoreIndex, Settings
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

load_dotenv()

# LLM and embedding model configuration
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.llm = GoogleGenAI(model="models/gemini-2.5-flash", temperature=0.1)

df = pd.read_csv("./src/data/icd10_index_extracted.csv")

icd10_documents = []

# Convert each row of the DataFrame into a Document object
for _, row in df.iterrows():
    code = row.get("code")
    main_term = row.get("main_term")
    title = row.get("title")
    path = row.get("path")

    # Ignore rows with missing codes
    if pd.isna(code) or code.strip() == "":
        continue

    # Texto principal usado para embedding
    text = f"Main term: {main_term}\nTitle: {title}\nICD-10 Code: {code}"

    metadata = {
        "code": code,
        "main_term": main_term,
        "title": title,
        "path": path
    }

    icd10_documents.append(Document(text=text, metadata=metadata))

print(f"Total documents created: {len(icd10_documents)}")

# Initialize Chroma client for vector storage
print("\nInitializing Chroma client...")
chroma_client = chromadb.PersistentClient("./chroma_store")
chroma_collection = chroma_client.get_or_create_collection("icd10_index")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Index the documents in the vector store
index = VectorStoreIndex.from_documents(
    icd10_documents,
    storage_context=storage_context,
    show_progress=True,
)

print(f"Total documents indexed: {len(icd10_documents)}")
