import os, re, json, requests
from dotenv import load_dotenv

load_dotenv()

API_KEY  = "testkey"
BASE_URL = "https://openrouter.ai/api/v1"

# langchain-openai reads these two names
os.environ["OPENAI_API_KEY"]  = API_KEY
os.environ["OPENAI_API_BASE"] = BASE_URL



# TOOL_MODEL = "meta-llama/llama-3.3-70b-instruct"   # tool calling: use this for agents
FAST_MODEL = "meta-llama/llama-3.1-8b-instruct"    # cheap, for plain text steps
TOOL_MODEL = "openai/gpt-5-mini"

TAVILY_KEY = os.getenv("TAVILY_API_KEY")           # optional

IS_LOCAL_MODEL = True

LOCAL_MODEL = "qwen3-coder:30b"