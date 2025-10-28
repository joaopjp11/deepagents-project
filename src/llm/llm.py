import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from src.tools.internet_search import internet_search
from src.tools.weather import get_weather

load_dotenv()
llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai", api_key=os.environ["GOOGLE_API_KEY"])

research_instructions = """You are an expert researcher. Your job is to conduct thorough research, and then write a polished report.\nYou have access to an internet search tool as your primary means of gathering information.\n## `internet_search`\nUse this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included."""

checkpointer=MemorySaver()

agent = create_deep_agent(
    model=llm,
    tools=[internet_search, get_weather],
    system_prompt=research_instructions,
    interrupt_on={
        "get_weather": {
            "allowed_decisions": ["approve", "edit", "reject"]
        },
    },
    checkpointer=checkpointer
)
