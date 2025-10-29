
import os
import pandas as pd
from llama_index.core import Document, StorageContext, VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from dotenv import load_dotenv
from getpass import getpass
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()
GOOGLE_API_KEY=os.environ["GOOGLE_API_KEY"]

if 'GOOGLE_API_KEY' not in os.environ:
    os.environ['GOOGLE_API_KEY'] = getpass('Enter your Gemini API key: ')
    
Settings.llm = GoogleGenAI(model="models/gemini-2.5-flash", temperature=0.1)
Settings.embed_model = GoogleGenAIEmbedding(model_name="models/embedding-001")

NUM_ICD10_CODES = 100

df = pd.read_csv('./src/data/icd10_tabular_extracted.csv')


NUM_ICD10_CODES = 100  
 
print(f"A converter as primeiras {NUM_ICD10_CODES} linhas em Document objects...")
 
subset_df = df.head(NUM_ICD10_CODES)
 
icd10_documents = []
 
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
 
print(f"Total de documentos criados: {len(icd10_documents)}")
 
print("\nExemplo de documento criado:")
print(icd10_documents[0].text)
print("--------------------------------------------------")
print("Metadata correspondente:")
print(icd10_documents[0].metadata)


# # Initialize ChromaDB
# chroma_client = chromadb.EphemeralClient()
# chroma_collection = chroma_client.create_collection("multi_source_medical")

# vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
# storage_context = StorageContext.from_defaults(vector_store=vector_store)

embed_model = GoogleGenAIEmbedding(model="models/embedding-001")
 
print("\nA inicializar cliente Chroma...")
chroma_client = chromadb.PersistentClient("./chroma_store")
 
chroma_collection = chroma_client.get_or_create_collection("icd10cm")
 
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
 
storage_context = StorageContext.from_defaults(vector_store=vector_store)



index = VectorStoreIndex.from_documents(
    icd10_documents,
    storage_context=storage_context,
    show_progress=True,
)

print("\n✅ Multi-source index created!")
print(f"   Total documents: {len(icd10_documents)}")
 


# print("🔧 Building multi-source index...")
# # Print first 10 rows
# for i, row in df.iterrows():
#     print(type(row))
#     print("\n📄 Next row:")


# icd10_documents = []

# for i, row in df.iterrows():
#     text = f"""ICD-10 Code: {row['code']}
# Description: {row['description']}
# Inclusion terms: {row['inclusion_terms']}
# Notes: {row['notes']}
# Chapter: {row['chapter_desc']}
# Section: {row['section_desc']}
# """

#     doc = Document(
#         text=text,
#         metadata={
#             'source': 'icd10',
#             'type': 'structured_code',
#             'code': row['code'],
#             'description': row['description'],
#             'doc_id': f"icd10_{i}"
#         }
#     )

#     icd10_documents.append(doc)

# print(f"✅ Created {len(icd10_documents)} ICD-10 documents")

# # Open the CSV file
# with open('icd10_tabular_extracted.csv', newline='', encoding='utf-8') as csvfile:
#     reader = csv.DictReader(csvfile)  # Reads rows as dictionaries
#     for row in reader:
#         print(row['code'], row['description'])

# icd10_documents = []
# for i in range(0, NUM_ICD10_CODES):
#         # Format as structured text
    
#     code_data=icd10_dataset[i]
#     text = f"""ICD-10 Code: {code_data['output']}
# Description: {code_data['input']}
# """
    
#     doc = Document(
#         text=text,
#         metadata={
#             'source': 'icd10',
#             'type': 'structured_code',
#             'code': code_data['output'],
#             'description': code_data['input'],
#             'doc_id': f"icd10_{i}",
#             'llm_instruction': code_data['instruction']
#         }
#     )
#     icd10_documents.append(doc)

# print(f"✅ Created {len(icd10_documents)} ICD-10 documents")
# print(f"\n📄 Sample:")
# print(icd10_documents[0].text)
# print(f"Metadata: {icd10_documents[0].metadata}")