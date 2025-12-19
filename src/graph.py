from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes import chatbot_node, rag_node

def route_entry(state: AgentState) -> str:
    return "rag" if state["is_returning_user"] else "chatbot"

def route_chatbot(state: AgentState) -> str:
    return "chatbot" if state["next_step"] != "complete" else END

def create_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("rag", rag_node)
    
    workflow.set_conditional_entry_point(route_entry, {"chatbot": "chatbot", "rag": "rag"})
    
    workflow.add_conditional_edges("chatbot", route_chatbot, {"chatbot": END, END: END})
    workflow.add_edge("rag", END)
    
    return workflow.compile()

graph = create_graph()
