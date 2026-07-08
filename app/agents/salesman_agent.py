from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from app.tools.registry import get_salesman_tools
from app.prompts.prompts import salesman_agent_prompt
from app.llms.ollama import get_salesman_llm

async def create_salesman_agent ():
    llm = get_salesman_llm()
    tools = await get_salesman_tools()

    return create_agent(
        model = llm,
        tools = tools,
        system_prompt = salesman_agent_prompt,

    )