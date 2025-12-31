from langgraph.graph import StateGraph, END
from src.models.state import AgentState
from src.graph.nodes import chatbot_node, rag_node, classifier_node
from langchain_core.messages import HumanMessage
from src.core.logging import get_logger

logger = get_logger(__name__)
# Routing berdasarkan kelengkapan data
def route_entry(state: AgentState) -> str:
    is_returning = state.get("is_returning_user", False)
    user_data = state.get("user_data", {})
    current_step = state.get("next_step", "nama")
    
    # logger.info(f"route_entry: is_returning={is_returning}, "
    #             f"has_data={bool(user_data)}, "
    #             f"current_step={current_step}")
    
    mandatory_fields = ["nama", "kota", "tanggal_lahir"]
    has_complete_mandatory = all(user_data.get(f) for f in mandatory_fields)
    
    # Returning user dengan data expired (Special Case) -> classifier
    if is_returning and not user_data and current_step == "complete":
        logger.info("route_entry: Returning user with expired data → classifier")
        return "classifier"
    
    # Mandatory field belum lengkap -> chatbot
    if not has_complete_mandatory:
        logger.info(f"route_entry: Mandatory incomplete → chatbot")
        return "chatbot"
    
    # Mandatory field sudah lengkap -> classifier
    logger.info("route_entry: Mandatory complete → classifier")
    return "classifier"

def route_by_intent(state: AgentState) -> str:
    current_step = state.get("next_step")
    user_data = state.get("user_data", {})
    is_returning = state.get("is_returning_user", False)

    # Jika user klik tombol "ramalan karir" (reset data session saat ini)
    user_msg = state["messages"][-1].content if state["messages"] else ""
    if "ramalan karir" in user_msg.lower():
        return "chatbot"
    
    # Jika is_returning=True DAN user_data kosong DAN next_step="complete" (user returning tapi data redis expired)
    if is_returning and not user_data and current_step == "complete":
        intent = state.get("intent", "answering")
        return "rag" if intent == "asking" else "chatbot"
    
    # Jika masih collect data
    if current_step and current_step != "complete":
        return "chatbot"
    
    # Jika mandatory belum lengkap
    mandatory_fields = ["nama", "kota", "tanggal_lahir"]
    mandatory_complete = all(user_data.get(f) for f in mandatory_fields)
    
    if not mandatory_complete and user_data: 
        return "chatbot"
    
    # Route berdasarkan intent
    intent = state.get("intent", "answering")
    return "rag" if intent == "asking" else "chatbot"

def route_chatbot(state: AgentState) -> str:
    # Logic agar langsung arahkan ke classifier saat chat pertama (solve agar tidak generate ramalan (jika data complete) tapi langsung ke RAG)
    messages = state.get("messages", [])
    if messages and isinstance(messages[-1], HumanMessage):
        return "classifier"
    return END

def create_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("classifier", classifier_node)
    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("rag", rag_node)
    
    workflow.set_conditional_entry_point(
        route_entry, 
        {"chatbot": "chatbot", "classifier": "classifier"}
    )
    
    workflow.add_conditional_edges(
        "classifier", 
        route_by_intent, 
        {"chatbot": "chatbot", "rag": "rag"}
    )
    
    workflow.add_conditional_edges(
        "chatbot", 
        route_chatbot, 
        {END: END, "classifier": "classifier"}
    )
    
    workflow.add_edge("rag", END)
    
    return workflow.compile()

graph = create_graph()