from langgraph.graph import StateGraph, END
from src.state import AgentState, UserData
from src.nodes import chatbot_node, fortune_teller_node

def should_continue(state: AgentState) -> str:
    """Determine if we should continue collecting or generate fortune"""
    user_data = state["user_data"]
    required_fields = ["name", "location", "dob", "job_field", "email"]
    
    if all(user_data.get(field) for field in required_fields):
        return "fortune"
    return "collect"

def create_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("fortune", fortune_teller_node)
    
    # Set entry point
    workflow.set_entry_point("chatbot")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "chatbot",
        should_continue,
        {
            "collect": END,
            "fortune": "fortune"
        }
    )
    
    # Fortune node leads to END
    workflow.add_edge("fortune", END)
    
    return workflow.compile()

# Create the compiled graph
graph = create_graph()
