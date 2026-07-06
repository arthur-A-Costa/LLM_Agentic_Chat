from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from app.tools.registry import salesman_tools
from app.prompts.prompts import salesman_agent_prompt
from app.llms.ollama import get_salesman_llm

def create_salesman_agent ():
    llm = get_salesman_llm()

    return create_agent(
        model = llm,
        tools = salesman_tools,
        system_prompt = salesman_agent_prompt,

    )