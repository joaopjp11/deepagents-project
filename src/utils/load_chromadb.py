import os
import subprocess

# Path to the ChromaDB SQLite database
CHROMA_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "chroma_store", "chroma.sqlite3"))

def ensure_chromadb_ready():
	if not os.path.exists(CHROMA_DB_PATH):
		print("\nChromaDB not found. The embedding generation process may take a while...\n")
		subprocess.run(["python", os.path.join(os.path.dirname(__file__), "data", "doc_generator.py")], check=True)
	else:
		print("\nChromaDB found and ready to use.\n")