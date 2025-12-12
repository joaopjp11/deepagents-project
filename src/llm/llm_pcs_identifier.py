import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from src.tools.icd10_search import search_icd10_code

load_dotenv()
llm = init_chat_model("gemini-2.5-flash-lite-preview-09-2025", model_provider="google_genai", api_key=os.environ["GOOGLE_API_KEY"])

coding_instructions = """You are a medical coding assistant.

Your ONLY task is to identify **medical procedures actually performed during this encounter/admission** from the clinical report. 
A "procedure" is an action performed on the patient during the current encounter that corresponds to an ICD-10-PCS procedure (e.g., surgeries, imaging studies, diagnostic procedures, device insertions, drainages, infusions, reductions, endoscopies).

DO NOT list:
- Diagnoses or differential diagnoses
- Medications or medication administration
- Lab tests, specimen collections, or blood draws
- Vital signs or monitoring
- Past medical history or prior procedures
- Physical exam findings
- Treatment plans or routine care
- Consultations unless a procedure was performed
- Anything **not clearly documented as done** during this encounter

You must return ONLY the names of the procedures actually performed, in **ICD-10-PCS nomenclature style**.

Output JSON example:
{
  "Medical procedures": [
    "Diagnostic Imaging, Brain, Computed Tomography (CT)"
  ]
}

If no procedures were performed:
{
  "Medical procedures": []
}

"""

checkpointer=MemorySaver()

agent = create_deep_agent(
    model=llm,
    tools=[search_icd10_code],
    system_prompt=coding_instructions,
    checkpointer=checkpointer
)