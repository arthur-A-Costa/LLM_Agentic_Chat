from typing import Literal, TypedDict, Annotated
import operator
import uuid

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AnyMessage, AIMessage

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages

from app.router import route_message
from app.agents.salesman_agent import create_salesman_agent
from app.agents.consultant_agent import create_consultant_agent
from app.agents.router_agent import router_message
from app.agents.reviewer_agent import create_reviewer_agent

import os

ENABLE_REVIEW_AGENT = os.getenv("ENABLE_REVIEW_AGENT", "true").lower() == "true"

# Creation of the class that works as the state - memory of the AI application
class ChatGraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    selected_agent: str
    router_reason: str
    draft_response: str
    response: str

salesmas_agent = create_salesman_agent()
consultant_agent = create_consultant_agent()
reviewer_agent = create_reviewer_agent()

def get_latest_user_message(state: ChatGraphState) -> str:
    for message in reversed(state["messages"]):
        if message.type == "human":
            return message.content
    return ""

def router_node(state: ChatGraphState) -> ChatGraphState:
    latest_message = get_latest_user_message(state)
    decision = router_message(latest_message)

    return{
        **state,
        "selected_agent": decision.selected_agent,
        "router_reason": decision.reason, 
    }

def choose_next_node(
    state: ChatGraphState,
) -> Literal["salesman", "consultant", "human_support"]:
    selected_agent = state["selected_agent"]

    if selected_agent == "human_support":
        return "human_support"

    if selected_agent == "salesman":
        return "salesman"

    return "consultant"

def salesman_node(state: ChatGraphState) -> ChatGraphState:
    
    result = salesmas_agent.invoke(
        {
              "messages": state["messages"]
        }
    )

    final_message = result["messages"][-1].content

    return {
         "messages": [final_message],
         "draft_response": final_message
    }

def consultant_node(state: ChatGraphState) -> ChatGraphState:
    
    result = consultant_agent.invoke(
        {
              "messages": state["messages"]
        }
    )

    final_message = result["messages"][-1].content

    return {
         "messages": [final_message],
         "draft_response": final_message
    }

def reviewer_node(state: ChatGraphState) -> ChatGraphState:
    draft_response = state["draft_response"]

    result = reviewer_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Review and rewrite the following draft answer before it is shown "
                        "to the customer. Preserve the meaning and factual details.\n\n"
                        f"Draft answer:\n{draft_response}"
                    ),
                }
            ]
        }
    )

    reviewed_message = result["messages"][-1]
    reviewed_text = reviewed_message.content

    return {
         "messages": [AIMessage(content=reviewed_text)],
         "response": reviewed_text,
    }

# Function that builds the graph - framework that defines the order in which agents/nodes are executed 
def build_graph(checkpointer):
    agent_builder = StateGraph(ChatGraphState)

    agent_builder.add_node("router", router_node)
    agent_builder.add_node("salesman", salesman_node)
    agent_builder.add_node("consultant", consultant_node)
    agent_builder.add_node("reviewer", reviewer_node)

    agent_builder.add_edge(START, "router")
    agent_builder.add_conditional_edges(
        "router",
        choose_next_node,
        {
            "salesman": "salesman",
            "consultant": "consultant"
        },
    )
    if ENABLE_REVIEW_AGENT:
        agent_builder.add_edge("salesman", "reviewer")
        agent_builder.add_edge("consultant", "reviewer")
        agent_builder.add_edge("reviewer", END)

    else:
        agent_builder.add_edge("salesman", END)
        agent_builder.add_edge("consultant", END)

    return agent_builder.compile(checkpointer=checkpointer)

checkpointer = InMemorySaver()

chatGraph = build_graph(checkpointer=checkpointer)