from fastapi import APIRouter, HTTPException
from src.models.query_request import QueryRequest
from src.models.interrupt_decision import InterruptDecisionRequest
from src.llm.llm_tool_index import agent
from langgraph.types import Command
from src.models.icd10_result import parse_icd10_result
import uuid

router = APIRouter()
config = {"configurable": {"thread_id": "some_id"}}

# Temporary storage for interrupts
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

        structured = parse_icd10_result(result["messages"][-1].content)

        return {"response": structured}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interrupt_decision")
async def interrupt_decision(request: InterruptDecisionRequest):
    interrupt = request.interrupt_id
    if not interrupt:
        raise HTTPException(status_code=404, detail="Interrupt not found")
    if request.decision == "approve":
        result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)
        structured = parse_icd10_result(result["messages"][-1].content)
        return {result}
    elif request.decision == "reject":
        return {"message": "Code rejected by human."}
    else:
        raise HTTPException(status_code=400, detail="Invalid decision")

@router.get("/")
def root():
    return {"message": "DeepAgents API is running!"}
