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
def chat(request: ChatRequest):
    """
    selected_agent = route_message(request.message)

    if selected_agent == "human_support":
            return {
                "agent": "human_support",
                "response": (
                    "This situation should be handled by human support. "
                    "Please contact the bank's official support channel immediately."
                ),
            }
    
    if selected_agent == "salesman":
         agent = salesman_agent
    else:
         agent = consultant_agent
    
    result = agent.invoke(
        {
              "messages": [ {
                   "role": "user",
                   "content": request.message,
            } ]
        }
    )

    final_message = result["messages"][-1].content
    """

    conversation_id = request.conversation_id or str(uuid.uuid4())[:255]

    config: RunnableConfig = {"configurable": {"thread_id": conversation_id}}
    result = chatGraph.invoke(
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