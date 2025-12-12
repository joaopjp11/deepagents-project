import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from src.tools.icd10_search import search_icd10_code

load_dotenv()
llm = init_chat_model("gemini-2.5-flash-lite-preview-09-2025", model_provider="google_genai", api_key=os.environ["GOOGLE_API_KEY"])

coding_instructions = """coding_instructions =
You are a medical coding assistant.
Your first task is to identify the procedures done to the patient, so that in the future you can chose the correct ICD10-pcs codes to associate with the patient. 
You should follow this guilines {guidelines}
, so that the semantical description you give to the pcs maches the description on the ICD10-pcs tables.
Return your answer strictly with the following format:
{
  "icd10_codes": ["A00", "A01.0",...],
  "confidence": 0.92,
  "notes": "Explain briefly why these ICD-10 codes were selected."
}
Where:
- 'icd10_codes' must be valid ICD-10 codes (if multiple, include all).
- 'confidence' is a float between 0 and 1 indicating certainty.
- 'notes' should be a medium explanation in text format, without the "\n" character.
"""

checkpointer=MemorySaver()

agent = create_deep_agent(
    model=llm,
    tools=[search_icd10_code],
    system_prompt=coding_instructions,
    interrupt_on={
        "search_icd10_code": {
            "allowed_decisions": ["approve", "reject"]
        },
    },
    checkpointer=checkpointer
)