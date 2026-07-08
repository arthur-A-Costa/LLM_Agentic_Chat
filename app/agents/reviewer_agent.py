from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from app.prompts.prompts import reviewer_agent_prompt
from app.llms.ollama import get_reviewer_llm

async def create_reviewer_agent ():
    llm = get_reviewer_llm()

    return create_agent(
        model = llm,
        tools = [],
        system_prompt = reviewer_agent_prompt,

    )