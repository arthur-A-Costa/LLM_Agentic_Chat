from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from app.prompts.prompts import editor_agent_prompt
from app.llms.ollama import get_editor_llm

async def create_editor_agent ():
    llm = get_editor_llm()

    return create_agent(
        model = llm,
        tools = [],
        system_prompt = editor_agent_prompt,

    )