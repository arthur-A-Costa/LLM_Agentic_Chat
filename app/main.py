from fastapi import FastAPI
from pydantic import BaseModel
import uuid

from langchain_core.runnables import RunnableConfig

from app.graph import build_graph, chatGraph
from app.agents.router_agent import router_message

app = FastAPI(title="Banking Agents API")

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    conversation_id: str 
    agent: str
    response: str

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "banking-agents-backend"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    conversation_id = request.conversation_id or str(uuid.uuid4())[:255]

    config: RunnableConfig = {"configurable": {"thread_id": conversation_id}}
    result = await chatGraph.ainvoke(
    {
        "messages": [
            {
                "role" : "user",
                "content" : request.message
             }
            ],
        "selected_agent": "",
        "router_reason": "",
        "draft_response": "",
        "response": "",
    },
    config=config
)

    return {
         "conversation_id": conversation_id,
         "agent": result["selected_agent"],
         "response": result["response"],
    }