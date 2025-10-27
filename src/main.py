import os
from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver


load_dotenv()
 
llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai", api_key=os.environ["GOOGLE_API_KEY"])

config = {"configurable": {"thread_id": "some_id"}} 


# Web search tool
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""

    return f"Search results for '{query}' (placeholder - max_results: {max_results}, topic: {topic}, include_raw_content: {include_raw_content})"

def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is sunny."

# System prompt to steer the agent to be an expert researcher
research_instructions = """You are an expert researcher. Your job is to conduct thorough research, and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

# Create the deep agent
agent = create_deep_agent(
    model=llm,
    tools=[internet_search, get_weather],
    system_prompt=research_instructions,
    checkpointer = MemorySaver(),
    interrupt_on={
    "get_weather": {
        "allowed_decisions": ["approve", "edit", "reject"]
    },
    }
)

# Invoke the agent
# result = agent.invoke({"messages": [{"role": "user", "content": "What is langgraph?"}]})
# print("Agent Response:")
# print(result['messages'][-1].content)

app = FastAPI(title="DeepAgents Research API")

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_model(request: QueryRequest):
    """Endpoint to ask the model a question."""
    try:
        result = agent.invoke({
            "messages": [{"role": "user", "content": request.question}]
        },
        config
        )
        result=agent.invoke(Command( resume={"decisions": [{"type": "approve"}]}  # or "edit", "reject"
    ), 
    config=config # Same thread ID to resume the paused conversation
)
        
        return {"response": result["messages"][-1].content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/")
def root():
    return {"message": "DeepAgents API is running!"}