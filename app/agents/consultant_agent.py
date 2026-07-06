from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from app.tools.registry import consultant_tools
from app.prompts.prompts import consultant_agent_prompt
from app.llms.ollama import get_consultant_llm 

def create_consultant_agent ():
    llm = get_consultant_llm()

    return create_agent(
        model = llm,
        tools = consultant_tools,
        system_prompt = consultant_agent_prompt,
    )