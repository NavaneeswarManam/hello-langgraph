from config import LOCAL_MODEL
from config import IS_LOCAL_MODEL
from config import API_KEY
from config import BASE_URL
from config import TOOL_MODEL
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

def llm(model=TOOL_MODEL, temperature=0):
    """A LangChain chat model pointed at OpenRouter."""
    if IS_LOCAL_MODEL is True:
        return ChatOllama(
            model=LOCAL_MODEL,
            temperature=temperature
        )
        
    return ChatOpenAI(model=model, temperature=temperature,
                      base_url=BASE_URL, api_key=API_KEY)

print(llm().invoke("Reply with just: ok").content)