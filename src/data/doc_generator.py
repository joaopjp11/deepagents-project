# ICD-10 document generator for vector indexing
# This script reads the first N codes from the extracted CSV file, creates Document objects and indexes them in ChromaDB

import pandas as pd
import chromadb
from dotenv import load_dotenv
from llama_index.core import Document, StorageContext, VectorStoreIndex, Settings
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.vector_stores.chroma import ChromaVectorStore

load_dotenv()

# LLM and embedding model configuration
Settings.llm = GoogleGenAI(model="models/gemini-2.5-flash", temperature=0.1)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/embedding-001")

df = pd.read_csv('./src/data/icd10_tabular_extracted.csv')

# Number of codes to convert to documents (test phase)
NUM_ICD10_CODES = 100

subset_df = df.head(NUM_ICD10_CODES)

icd10_documents = []

# Convert each row of the DataFrame into a Document object
for _, row in subset_df.iterrows():
    text = (
        f"Code: {row.get('code')}\n"
        f"Description: {row.get('description')}\n"
        f"Chapter: {row.get('chapter')} - {row.get('chapter_desc')}\n"
        f"Section: {row.get('section')} - {row.get('section_desc')}"
    )

    metadata = {
        "code": row.get("code"),
        "description": row.get("description"),
        "chapter": row.get("chapter"),
        "section": row.get("section"),
        "inclusion_terms": row.get("inclusion_terms"),
        "includes": row.get("includes"),
        "excludes1": row.get("excludes1"),
        "excludes2": row.get("excludes2"),
        "use_additional_code": row.get("use_additional_code"),
        "code_first": row.get("code_first"),
        "notes": row.get("notes"),
        "parent_codes": row.get("parent_codes")
    }

    icd10_documents.append(Document(text=text, metadata=metadata))

print(f"Total documents created: {len(icd10_documents)}")

# Initialize Chroma client for vector storage
print("\nInitializing Chroma client...")
chroma_client = chromadb.PersistentClient("./chroma_store")
chroma_collection = chroma_client.get_or_create_collection("icd10cm")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Index the documents in the vector store
index = VectorStoreIndex.from_documents(
    icd10_documents,
    storage_context=storage_context,
    show_progress=True,
)

print(f"Total documents indexed: {len(icd10_documents)}")