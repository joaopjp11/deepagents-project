from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from dotenv import load_dotenv
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI
import chromadb
import os

load_dotenv()

Settings.llm = GoogleGenAI(model="models/gemini-2.5-flash-lite-preview-09-2025", temperature=0.1)

CHROMA_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "chroma_store"))

# Initialize Chroma client
chroma_client = chromadb.PersistentClient(CHROMA_DB_PATH)

# Setup for ICD-10 Tabular data (original collection) with Google embeddings
google_embed_model = GoogleGenAIEmbedding(model_name="models/embedding-001")
chroma_collection_tabular = chroma_client.get_or_create_collection("icd10cm")
vector_store_tabular = ChromaVectorStore(chroma_collection=chroma_collection_tabular)
storage_context_tabular = StorageContext.from_defaults(vector_store=vector_store_tabular)

# Temporarily set Google embeddings for tabular index
Settings.embed_model = google_embed_model
index_tabular = VectorStoreIndex.from_vector_store(
    vector_store=vector_store_tabular,
    storage_context=storage_context_tabular
)

# Setup for ICD-10 Index data (new collection) with HuggingFace embeddings
huggingface_embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
chroma_collection_index = chroma_client.get_or_create_collection("icd10_index")
vector_store_index = ChromaVectorStore(chroma_collection=chroma_collection_index)
storage_context_index = StorageContext.from_defaults(vector_store=vector_store_index)

# Temporarily set HuggingFace embeddings for index
Settings.embed_model = huggingface_embed_model
index_index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store_index,
    storage_context=storage_context_index
)

# Create query engines for both sources
query_engine_tabular = index_tabular.as_query_engine()
query_engine_index = index_index.as_query_engine()

# Reset to default embedding model
Settings.embed_model = google_embed_model

def parse_multiple_conditions(input_text: str):
    """
    Parse input text to identify multiple medical conditions.
    Splits on common separators and cleans up each condition.
    """
    import re
    
    # Common separators for multiple conditions
    separators = [
        r',\s*(?=[A-Z])',  # Comma followed by capital letter
        r';\s*',           # Semicolon
        r'\.\s*(?=[A-Z])', # Period followed by capital letter
        r'\s*-\s*(?=[A-Z])', # Dash separating conditions
    ]
    
    conditions = [input_text.strip()]
    
    for separator in separators:
        new_conditions = []
        for condition in conditions:
            parts = re.split(separator, condition)
            new_conditions.extend([part.strip() for part in parts if part.strip()])
        conditions = new_conditions
    
    # Filter out very short conditions (likely artifacts)
    conditions = [c for c in conditions if len(c) > 10]
    
    return conditions

def search_icd10_code(symptoms: str):
    """
    Receives symptoms and returns the most relevant ICD-10 code by combining 
    results from both ICD-10 Tabular and Index data sources for comprehensive 
    medical coding accuracy. Now supports multiple conditions in a single input.
    """
    # Parse input for multiple conditions
    conditions = parse_multiple_conditions(symptoms)
    
    all_codes = []
    all_confidences = []
    all_notes = []
    
    print(f"Detected {len(conditions)} condition(s):")
    for i, condition in enumerate(conditions, 1):
        print(f"  {i}. {condition[:60]}{'...' if len(condition) > 60 else ''}")
    
    # Process each condition separately
    for condition_idx, condition in enumerate(conditions):
        print(f"\nProcessing condition {condition_idx + 1}: {condition[:50]}...")
        
        # Search in ICD-10 Tabular data (detailed descriptions)
        response_tabular = query_engine_tabular.query(condition)
        
        # Search in ICD-10 Index data (alphabetical index)
        response_index = query_engine_index.query(condition)
        
        # Combine results from both sources for this condition
        condition_codes = []
        condition_confidences = []
        condition_notes = []
        
        # Process Tabular results
        for source in response_tabular.source_nodes:
            code = source.metadata.get("code", "Unknown")
            confidence = round(source.score, 3)
            note = f"Tabular Match: {code}. Condition {condition_idx + 1}: {condition[:30]}..."
            
            condition_codes.append(code)
            condition_confidences.append(confidence)
            condition_notes.append(note)
        
        # Process Index results
        for source in response_index.source_nodes:
            code = source.metadata.get("code", "Unknown")
            confidence = round(source.score, 3)
            note = f"Index Match: {code}. Condition {condition_idx + 1}: {condition[:30]}..."
            
            # Only add if not already present from tabular results
            if code not in condition_codes:
                condition_codes.append(code)
                condition_confidences.append(confidence)
                condition_notes.append(note)
        
        # Take top 2-3 results per condition to avoid overwhelming
        max_per_condition = 3 if len(conditions) > 1 else 5
        
        if condition_confidences:
            sorted_condition_results = sorted(
                zip(condition_codes, condition_confidences, condition_notes),
                key=lambda x: x[1],
                reverse=True
            )[:max_per_condition]
            
            # Add to overall results
            for code, confidence, note in sorted_condition_results:
                if code not in all_codes:  # Avoid duplicates across conditions
                    all_codes.append(code)
                    all_confidences.append(confidence)
                    all_notes.append(note)
    
    # Sort all results by confidence score (highest first)
    if all_confidences:
        final_sorted_results = sorted(
            zip(all_codes, all_confidences, all_notes),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Unpack sorted results
        all_codes, all_confidences, all_notes = zip(*final_sorted_results)
        all_codes = list(all_codes)
        all_confidences = list(all_confidences)
        all_notes = list(all_notes)
    
    print(f"Found {len(all_codes)} total unique codes across all conditions")
    
    return {
        "icd10_codes": all_codes,
        "confidence": all_confidences,
        "notes": all_notes
    }
