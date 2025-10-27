from fastapi import APIRouter, HTTPException
from src.models.query_request import QueryRequest
from src.llm.llm import agent
from langgraph.types import Command

router = APIRouter()
config = {"configurable": {"thread_id": "some_id"}}

@router.post("/ask")
async def ask_model(request: QueryRequest):
    try:
        result = agent.invoke({
            "messages": [{"role": "user", "content": request.question}]
        }, config)
        result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)
        return {"response": result["messages"][-1].content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def root():
    return {"message": "DeepAgents API is running!"}
