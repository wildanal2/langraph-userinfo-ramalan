from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes import chatbot_node, rag_node, classifier_node

def route_entry(state: AgentState) -> str:
    if state["is_returning_user"]:
        return "classifier"
    return "chatbot"

def route_by_intent(state: AgentState) -> str:
    mandatory_fields = ["nama", "kota", "tanggal_lahir"]
    mandatory_complete = all(state["user_data"].get(f) for f in mandatory_fields)
    
    if not mandatory_complete:
        return "chatbot"
    
    user_msg = state["messages"][-1].content if state["messages"] else ""
    if "ramalan karir" in user_msg.lower():
        return "chatbot"
    
    return "rag" if state.get("intent") == "asking" else "chatbot"

def route_chatbot(state: AgentState) -> str:
    return END

def create_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("classifier", classifier_node)
    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("rag", rag_node)
    
    workflow.set_conditional_entry_point(route_entry, {"chatbot": "chatbot", "classifier": "classifier"})
    
    workflow.add_conditional_edges("classifier", route_by_intent, {"chatbot": "chatbot", "rag": "rag"})
    workflow.add_conditional_edges("chatbot", route_chatbot, {END: END})
    workflow.add_edge("rag", END)
    
    return workflow.compile()

graph = create_graph()
