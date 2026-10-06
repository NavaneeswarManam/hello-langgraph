from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]