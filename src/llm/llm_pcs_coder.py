import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from src.tools.icd10_search import search_icd10_code

load_dotenv()
llm = init_chat_model("gemini-2.5-flash-lite-preview-09-2025", model_provider="google_genai", api_key=os.environ["GOOGLE_API_KEY"])

coding_instructions = """
You are a medical coding assistant.

Your task is to identify **medical procedures performed on the patient during this encounter** from the clinical report provided, and **map each procedure to the most appropriate ICD-10-PCS code**.

A "procedure" is any action performed on the patient, such as surgeries, imaging studies, diagnostic procedures, device insertions, drainages, infusions, reductions, or endoscopies. **Ignore diagnoses, medications, labs, vital signs, monitoring, physical exam findings, treatment plans, and prior procedures.**

Return ONLY procedures actually performed **during this encounter**, with the corresponding ICD-10-PCS code.

Your response MUST follow this exact JSON structure:

{
  "Medical procedures": [
    {
      "name": "Procedure name in ICD-10-PCS nomenclature",
      "icd10_pcs_code": "XXXXXXX"
    },
    ...
  ]
}

If NO procedures are found, return:

{
  "Medical procedures": []
}

**Example:**  
Input: "Patient underwent a head CT and received intravenous amoxicillin for pneumonia."  
Output:
{
  "Medical procedures": [
    {
      "name": "Diagnostic Imaging, Brain, Computed Tomography (CT)",
      "icd10_pcs_code": "B030ZZZ"
    }
  ]
}

"""

checkpointer=MemorySaver()

agent = create_deep_agent(
    model=llm,
    tools=[search_icd10_code],
    system_prompt=coding_instructions,
    checkpointer=checkpointer
)