from pydantic import BaseModel

class InterruptDecisionRequest(BaseModel):
    interrupt_id: str
    decision: str 