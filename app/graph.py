from typing import Literal, TypedDict, Annotated
import operator
import uuid
from pydantic import BaseModel

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AnyMessage, AIMessage

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row

from app.utils.router import route_message
from app.agents.salesman_agent import create_salesman_agent
from app.agents.consultant_agent import create_consultant_agent
from app.agents.router_agent import router_message
from app.agents.reviewer_agent import create_reviewer_agent
from app.agents.editor_agent import create_editor_agent

import os

ENABLE_REVIEW_AGENT = os.getenv("ENABLE_REVIEW_AGENT", "true").lower() == "true"
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres_user:postgres_password@postgres:5432/postgres")

# Creation of the class that works as the state - memory of the AI application
class ChatGraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    selected_agent: str
    router_reason: str
    draft_response: str
    response: str
    review_action: str
    review_text: list[str]

# Can be used in teh future for structured review responses
class ReviewResult(BaseModel):
    passed: bool
    severity: Literal["none", "minor", "major"]
    issues: list[str]
    recommended_action: Literal["return", "edit", "redo"]

# salesmas_agent = create_salesman_agent()
# consultant_agent = create_consultant_agent()
# reviewer_agent = create_reviewer_agent()

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

async def salesman_node(state: ChatGraphState) -> ChatGraphState:
    
    salesmas_agent = await create_salesman_agent()
    result = await salesmas_agent.ainvoke(
        {
              "messages": state["messages"]
        }
    )

    final_message = result["messages"][-1].content

    return {
         "messages": [AIMessage(content=final_message)],
         "draft_response": final_message,
         "response": final_message
    }

async def consultant_node(state: ChatGraphState) -> ChatGraphState:
    
    consultant_agent = await create_consultant_agent()
    result = await consultant_agent.ainvoke(
        {
              "messages": state["messages"]
        }
    )

    final_message = result["messages"][-1].content

    return {
         "messages": [AIMessage(content=final_message)],
         "draft_response": final_message,
         "response": final_message
    }

async def reviewer_node(state: ChatGraphState) -> ChatGraphState:
    draft_response = state["draft_response"]
    latest_user_message = get_latest_user_message(state)

    reviewer_agent = await create_reviewer_agent()
    # "Return structured output in the form of Json that utilizes the following values (following the respective data type):\n"
    result = await reviewer_agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Review and analyze the following draft answer before it is shown "
                        "to the customer and make sure it completely answers the users last message "
                        "and contains no gramatical mistakes or other issues.\n\n"
                        "Return one of the following actions:"
                        "- return"
                        "- edit"
                        "Choose 'return' if the answer is acceptable and meets all requirements"
                        "Choose 'edit' in cases such as:"
                        "- The text is not in the same language as the question"
                        "- The grammar or formatting is poor or incorrect"
                        "- The answer needs to be refined or made clearer"
                        "- The response cites internal functions, product codes, or other information that should be hidden from the public"
                        f"Last user message:\n{latest_user_message}\n"
                        f"Draft answer:\n{draft_response}\n"
                        "Response Format:\n"
                        "passed: <True or False>\n"
                        "severity: <none , minor, medium, major> based on amount of errors and issues\n"
                        "issues:  <short list of issues or none>\n"
                        "recommended_action: <return or edit>"
                    ),
                }
            ]
        }
    )

    reviewer_message = result["messages"][-1].content.strip()
    lower = reviewer_message.lower()
    if "recommended_action: edit" in lower:
        review_action = "edit"
    else:
        review_action = "return"

    return {
        "review_action": review_action,
        "review_text": [reviewer_message],
    }

def review_decision_node(state):
    review = state["review_action"]

    if review == "return":
        return "final"

    if review == "edit":
        return "editor"

    #if review.recommended_action == "redo" and state["redo_count"] < 1:
    #    return "redo_specialist"

    return "final"

async def editor_node(state: ChatGraphState) -> ChatGraphState:
    draft_response = state["draft_response"]
    latest_user_message = get_latest_user_message(state)
    review_issues = state["review_text"]

    editor_agent = await create_editor_agent()
    result = await editor_agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Edit and reformat the following draft answer before it is shown "
                        "to the customer.\n"
                        "Follow the issues found by the reviwer as a guideline of possible issues to fix\n\n"
                        "User question:\n"
                        f"{latest_user_message}\n\n"
                        "Reviewer issues:\n"
                        f"{review_issues}\n\n"
                        "Draft answer:\n"
                        f"{draft_response}"
                    ),
                }
            ]
        }
    )

    edited_message = result["messages"][-1]
    edited_text = edited_message.content

    return {
         "messages": [AIMessage(content=edited_text)],
         "response": edited_text,
    }

def final_response_node(state: ChatGraphState) -> dict:
    return {
        "response": state["draft_response"]
    }

# Function that builds the graph - framework that defines the order in which agents/nodes are executed 
def build_graph(checkpointer):
    agent_builder = StateGraph(ChatGraphState)

    agent_builder.add_node("router", router_node)
    agent_builder.add_node("salesman", salesman_node)
    agent_builder.add_node("consultant", consultant_node)
    agent_builder.add_node("reviewer", reviewer_node)
    agent_builder.add_node("editor", editor_node)
    agent_builder.add_node("final_response", final_response_node)

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
        agent_builder.add_conditional_edges(
            "reviewer", 
            review_decision_node,
            {
                "final": "final_response",
                "editor": "editor",
            }
        )
        agent_builder.add_edge("final_response", END)
        agent_builder.add_edge("editor", END)

    else:
        agent_builder.add_edge("salesman", END)
        agent_builder.add_edge("consultant", END)

    return agent_builder.compile(checkpointer=checkpointer)

async def create_chat_graph(postgres_pool: AsyncConnectionPool):

    checkpointer = AsyncPostgresSaver(postgres_pool)
    await checkpointer.setup()

    chat_graph = build_graph(checkpointer=checkpointer)
    return chat_graph, postgres_pool