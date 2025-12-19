from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class UserData(TypedDict, total=False):
    nama: str | None
    kota: str | None
    tanggal_lahir: str | None
    bidang_ekraf: str | None
    jumlah_komunitas_ekraf_disekitar: str | None
    email: str | None
    no_telepon: str | None
    harapan: str | None

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_data: UserData
    next_step: str
    session_id: str
    is_returning_user: bool
    intent: str
    fortune_full: str
    interactive_options: dict | None
