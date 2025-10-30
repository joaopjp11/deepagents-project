from fastapi import FastAPI
from src.routers.agent_routers import router as agent_router

app = FastAPI(title="DeepAgents Research API")
app.include_router(agent_router)