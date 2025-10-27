import os
from typing import Literal
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()
 
llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai", api_key=os.environ["GOOGLE_API_KEY"])

# Web search tool
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""

    return f"Search results for '{query}' (placeholder - max_results: {max_results}, topic: {topic}, include_raw_content: {include_raw_content})"


# System prompt to steer the agent to be an expert researcher
research_instructions = """You are an expert researcher. Your job is to conduct thorough research, and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

# Create the deep agent
agent = create_deep_agent(
    model=llm,
    tools=[internet_search],
    system_prompt=research_instructions,
)

# Invoke the agent
result = agent.invoke({"messages": [{"role": "user", "content": "What is langgraph?"}]})
print("Agent response:")
print(result['messages'])
#print((result['messages'][0]).content)