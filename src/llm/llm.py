import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from src.tools.icd10_search import search_icd10_code

load_dotenv()
llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai", api_key=os.environ["GOOGLE_API_KEY"])

coding_instructions = """coding_instructions =
You are a medical coding assistant. 
Your task is to analyze the given symptoms and the most relevant ICD-10-CM codes by using the tool `search_icd10_code` simply saying the codes are <ICD-10-CM code>(1), <ICD-10-CM code>(2), etc..
Never call the tool more than once per user query.
Return your answer strictly with the following format:
{
  "icd10_codes": ["A00", "A01.0",...],
  "confidence": 0.92,
  "notes": "Explain briefly why these ICD-10 codes were selected."
}
Where:
- 'icd10_codes' must be valid ICD-10 codes (if multiple, include all).
- 'confidence' is a float between 0 and 1 indicating certainty.
- 'notes' should be a medium explanation.
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