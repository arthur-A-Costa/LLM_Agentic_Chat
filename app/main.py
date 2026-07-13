from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from pydantic import BaseModel
import uuid

from langchain_core.runnables import RunnableConfig

from app.graph import create_chat_graph
from app.agents.router_agent import router_message
from app.db.chat_history import save_message, create_conversation, load_messages

@asynccontextmanager
async def lifespan(app: FastAPI):
    chat_graph, postgres_pool = await create_chat_graph()

    app.state.chat_graph = chat_graph
    app.state.postgres_pool = postgres_pool

    yield

    await postgres_pool.close()

app = FastAPI(lifespan=lifespan)

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
async def chat(chat_request: ChatRequest, http_request: Request):
    conversation_id = chat_request.conversation_id or str(uuid.uuid4())[:255]

    create_conversation(conversation_id)
    save_message(
        conversation_id=conversation_id,
        role="user",
        content= chat_request.message,
    )

    config: RunnableConfig = {"configurable": {"thread_id": conversation_id}}
    result = await http_request.app.state.chat_graph.ainvoke(
    {
        "messages": [
            {
                "role" : "user",
                "content" : chat_request.message
             }
            ],
        "selected_agent": "",
        "router_reason": "",
        "draft_response": "",
        "response": "",
    },
    config=config
)

    save_message(
        conversation_id=conversation_id,
        role="assistant",
        content= result["response"],
        agent= result["selected_agent"]
    )

    return {
         "conversation_id": conversation_id,
         "agent": result["selected_agent"],
         "response": result["response"],
    }

@app.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(conversation_id: str):
    return {
        "conversation_id": conversation_id,
        "messages": load_messages(conversation_id),
    }