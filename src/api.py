from fastapi import FastAPI
from src.routers.agent_routers import router as agent_router
from src.utils.load_chromadb import ensure_chromadb_ready

# Ensure ChromaDB is ready before starting the API
# ensure_chromadb_ready()

app = FastAPI(title="DeepAgents Research API")
app.include_router(agent_router)