from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class UserData(TypedDict, total=False):
    name: str | None
    location: str | None
    dob: str | None
    job_field: str | None
    email: str | None

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_data: UserData
    next_step: str
