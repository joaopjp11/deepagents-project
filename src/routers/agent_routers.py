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

        if result.get("__interrupt__"):
            # Extract interrupt information
            interrupts = result["__interrupt__"][0].value
            action_requests = interrupts["action_requests"]
            review_configs = interrupts["review_configs"]

            # Create a lookup map from tool name to review config
            config_map = {cfg["action_name"]: cfg for cfg in review_configs}

            # Display the pending actions to the user
            for action in action_requests:
                review_config = config_map[action["name"]]
                print(f"Tool: {action['name']}")
                print(f"Arguments: {action['args']}")
                print(f"Allowed decisions: {review_config['allowed_decisions']}")
            return {
            "interrupt_id": "some_id",
            "message": "Interrupt forced. Awaiting human decision."
            }

        return {"response": result["messages"][-1].content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interrupt_decision")
async def interrupt_decision(request: InterruptDecisionRequest):
    interrupt = request.interrupt_id
    if not interrupt:
        raise HTTPException(status_code=404, detail="Interrupt not found")
    if request.decision == "approve":
        # Continua o fluxo
        result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)
        return {"response": result["messages"][-1].content}
    elif request.decision == "reject":
        return {"message": "Pergunta rejeitada pelo humano."}
    else:
        raise HTTPException(status_code=400, detail="Decisão inválida")

@router.get("/")
def root():
    return {"message": "DeepAgents API is running!"}
