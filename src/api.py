from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from src.graph import graph
from src.state import UserData

app = FastAPI(title="Creative Fortune Teller API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_state: dict | None = None

class ChatResponse(BaseModel):
    response: str
    user_data: dict
    is_complete: bool
    session_state: dict

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Initialize or restore state
        if request.session_state:
            state = request.session_state
        else:
            state = {
                "messages": [],
                "user_data": {
                    "name": None,
                    "location": None,
                    "dob": None,
                    "job_field": None,
                    "email": None
                },
                "next_step": "name"
            }
        
        # Add user message
        state["messages"].append(HumanMessage(content=request.message))
        
        # Run graph
        result = graph.invoke(state)
        
        # Extract AI response
        ai_response = result["messages"][-1].content if result["messages"] else "..."
        
        is_complete = result["next_step"] == "complete"
        
        return ChatResponse(
            response=ai_response,
            user_data=result["user_data"],
            is_complete=is_complete,
            session_state=result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/reset")
async def reset():
    """Reset conversation state"""
    return {
        "messages": [],
        "user_data": {
            "name": None,
            "location": None,
            "dob": None,
            "job_field": None,
            "email": None
        },
        "next_step": "name"
    }
