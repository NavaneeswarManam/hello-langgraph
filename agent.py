from tools import get_weather, web_search
from config import TOOL_MODEL
from llm import llm
from agent_state import AgentState
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, END


class Agent:
    def __init__(self, model, tools, system="", checkpointer=None,
                 interrupt_before=None, state_schema=AgentState):
        self.system = system

        graph = StateGraph(state_schema)
        graph.add_node("llm", self.call_llm)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges(
            "llm", self.exists_action, {True: "action", False: END})
        graph.add_edge("action", "llm")          # <- the cycle
        graph.set_entry_point("llm")

        self.graph = graph.compile(checkpointer=checkpointer,
                                   interrupt_before=interrupt_before or [])
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    # node: ask the model what to do next
    def call_llm(self, state):
        messages = state["messages"]
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        return {"messages": [self.model.invoke(messages)]}

    # conditional edge: did it ask for a tool?
    def exists_action(self, state):
        return len(state["messages"][-1].tool_calls) > 0

    # node: run every tool the model asked for
    def take_action(self, state):
        tool_calls = state["messages"][-1].tool_calls
        results = []
        for t in tool_calls:
            print(f"   calling: {t['name']}({t['args']})")
            if t["name"] not in self.tools:
                result = "bad tool name, retry"      # models do hallucinate tools
            else:
                result = self.tools[t["name"]].invoke(t["args"])
            results.append(ToolMessage(tool_call_id=t["id"], name=t["name"],
                                       content=str(result)))
        print("   back to the model")
        return {"messages": results}

        
prompt = """You are a smart research assistant. Use the tools to look things up.
You are allowed to make multiple calls, either together or in sequence.
Only look up information when you are sure of what you want."""

tools = [get_weather, web_search]

abot = Agent(llm(TOOL_MODEL), tools, system=prompt)

result = abot.graph.invoke(
    {"messages": [HumanMessage(content="What is the weather in Mumbai?")]})
print(result["messages"][-1].content)

import os
from IPython.display import Image

# 1. Define your folder and file path
output_folder = "./output_images"
file_path = os.path.join(output_folder, "graph.png")

# 2. Automatically create the folder if it doesn't exist yet
os.makedirs(output_folder, exist_ok=True)

# 3. Write the raw PNG binary data to the folder
png_data = abot.graph.get_graph().draw_png()
with open(file_path, "wb") as f:
    f.write(png_data)

# 4. Display the saved image in your notebook using the file path
Image(filename=file_path)