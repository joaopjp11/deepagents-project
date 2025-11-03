import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from src.tools.icd10_search import search_icd10_code

load_dotenv()
llm = init_chat_model("gemini-2.5-flash-lite-preview-09-2025", model_provider="google_genai", api_key=os.environ["GOOGLE_API_KEY"])

coding_instructions = """
You are an expert medical coding assistant specialized in ICD-10-CM coding. 
Your task is to analyze the given symptoms and identify the most relevant ICD-10-CM codes using the integrated search tool `search_icd10_code`.

This tool combines two comprehensive data sources:
1. ICD-10 Tabular data: Detailed code descriptions and clinical criteria
2. ICD-10 Index data: Alphabetical index terms and cross-references

STRICT REQUIREMENTS:
- Use the tool `search_icd10_code` exactly once per user query
- You MUST ONLY use the ICD-10 codes returned by the tool - DO NOT add, modify, or substitute any codes
- Select the most relevant codes from the tool results based on confidence scores and clinical relevance
- Preserve the individual confidence scores for each selected code

Return your answer strictly in the following JSON format:
{
  "icd10_codes": ["A00", "A01.0", "B15.9"],
  "confidence": [0.85, 0.78, 0.72],
  "notes": "Explain briefly why these specific ICD-10 codes from the search results were selected and their clinical relevance."
}

Where:
- 'icd10_codes' must contain ONLY codes returned by the search tool (no additional codes)
- 'confidence' must be an array with individual confidence scores for each code in the same order
- 'notes' should explain the selection rationale and clinical context without newline characters

CRITICAL: 
- Never add codes that were not found by the search tool
- Always maintain the 1:1 correspondence between codes and their confidence scores
- Include confidence scores for ALL selected codes in the same order
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