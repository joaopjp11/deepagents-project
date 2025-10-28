from fastapi import APIRouter, HTTPException
from src.models.query_request import QueryRequest
from src.models.interrupt_decision import InterruptDecisionRequest
from src.llm.llm import agent
from langgraph.types import Command
import uuid

router = APIRouter()
config = {"configurable": {"thread_id": "some_id"}}

# Armazenamento temporário dos interrupts
interrupt_store = {}

@router.post("/ask")
async def ask_model(request: QueryRequest):
    try:
        result = agent.invoke({
            "messages": [{"role": "user", "content": request.question}]
        }, config)
        # Ocorre sempre interrupt
        interrupt_id = str(uuid.uuid4())
        interrupt_store[interrupt_id] = result
        return {
            "interrupt_id": interrupt_id,
            "message": "Interrupt forced. Awaiting human decision."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interrupt_decision")
async def interrupt_decision(request: InterruptDecisionRequest):
    interrupt = interrupt_store.get(request.interrupt_id)
    if not interrupt:
        raise HTTPException(status_code=404, detail="Interrupt not found")
    if request.decision == "approve":
        # Continua o fluxo
        result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)
        del interrupt_store[request.interrupt_id]
        return {"response": result["messages"][-1].content}
    elif request.decision == "reject":
        del interrupt_store[request.interrupt_id]
        return {"message": "Pergunta rejeitada pelo humano."}
    else:
        raise HTTPException(status_code=400, detail="Decisão inválida")

@router.get("/")
def root():
    return {"message": "DeepAgents API is running!"}
