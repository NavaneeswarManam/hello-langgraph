from config import TAVILY_KEY
import requests
from langchain_core.tools import tool

def _tavily(query, max_results=3):
    r = requests.post("https://api.tavily.com/search",
                      json={"api_key": TAVILY_KEY, "query": query,
                            "max_results": max_results},
                      timeout=30).json()
    return [x["content"] for x in r.get("results", [])]

def _ddg(query, max_results=3):
    # pyrefly: ignore [missing-import]
    from ddgs import DDGS                      # pip install ddgs
    with DDGS() as d:
        return [r["body"] for r in d.text(query, max_results=max_results)]

def raw_search(query, max_results=3):
    """Plain function (not a tool) so the essay writer can call it directly."""
    backends = ([_tavily] if TAVILY_KEY else []) + [_ddg]
    for b in backends:
        try:
            hits = b(query, max_results)
            if hits:
                return hits
        except Exception as e:
            print(f"   (search backend {b.__name__} failed: {e})")
    return [f"No search results available for: {query}"]


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city. Use this for any question about
    weather, temperature, or how warm somewhere is."""
    j = requests.get(f"https://wttr.in/{city}", params={"format": "j1"}, timeout=25).json()
    c = j["current_condition"][0]
    return f"{city}: {c['temp_C']}C, {c['weatherDesc'][0]['value']}, humidity {c['humidity']}%"


@tool
def web_search(query: str) -> str:
    """Search the web for facts, news, and figures. Returns the top snippets."""
    return "\n---\n".join(raw_search(query, max_results=3))


tools = [get_weather, web_search]
print(get_weather.invoke({"city": "San Francisco"}))