from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from src.graph import graph
from src.redis_client import get_user_data, delete_user_data
import json
import asyncio
import uuid

app = FastAPI(title="Creative Fortune Teller API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StartRequest(BaseModel):
    session_id: str | None = None

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    session_state: dict | None = None

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/start-message")
async def start_message(request: StartRequest):
    from langchain_aws import ChatBedrock
    from src.config import settings
    
    async def generate():
        try:
            session_id = request.session_id or str(uuid.uuid4())
            user_data = get_user_data(session_id)
            
            llm = ChatBedrock(model_id=settings.bedrock_model_id, region_name=settings.aws_region)

            if user_data:
                # Skenario: User Lama (Returning)
                prompt = (
                    f"Generate a short, friendly greeting in Indonesian for a returning user named '{user_data.get('nama', 'User')}'. "
                    "Welcome them back to the creative economy platform and ask how you can help. "
                    "Strict rules: Max 3 sentences. Output ONLY the raw text message. Do not use markdown, headers, or quotes."
                )
            else:
                # Skenario: User Baru (New)
                prompt = (
                    "Generate a short, friendly welcome message in Indonesian for a new user on a creative economy platform. "
                    "Ask for their name to get started. "
                    "Strict rules: Max 3 sentences. Output ONLY the raw text message. Do not use markdown, headers, or quotes."
                )
            
            for chunk in llm.stream([HumanMessage(content=prompt)]):
                yield f"data: {json.dumps({'content': chunk.content, 'done': False})}\n\n"
                await asyncio.sleep(0.01)
            
            has_nama = user_data and user_data.get("nama") if user_data else False
            
            interactive_options = None
            if has_nama:
                interactive_options = {"type": "fortune_trigger", "text": "🔮 Ramalan Karir"}
            
            final_data = {
                "content": "",
                "done": True,
                "session_id": session_id,
                "is_returning_user": user_data is not None,
                "user_data": user_data or {},
                "interactive_options": interactive_options
            }
            yield f"data: {json.dumps(final_data)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        try:
            session_id = request.session_id or str(uuid.uuid4())
            user_data = get_user_data(session_id)
            is_returning = user_data is not None
            
            if request.session_state:
                state = request.session_state
                if state.get("messages") and isinstance(state["messages"][0], dict):
                    state["messages"] = [
                        HumanMessage(content=m["content"]) if m["type"] == "human" 
                        else AIMessage(content=m["content"]) 
                        for m in state["messages"]
                    ]
            else:
                state = {
                    "messages": [],
                    "user_data": user_data or {},
                    "next_step": "nama",
                    "session_id": session_id,
                    "is_returning_user": is_returning,
                    "intent": "answering"
                }
            
            state["messages"].append(HumanMessage(content=request.message))
            state["session_id"] = session_id
            state["is_returning_user"] = is_returning
            
            result = graph.invoke(state)
            
            ai_response = result["messages"][-1].content if result["messages"] else "..."
            is_complete = result.get("next_step") == "complete"
            
            words = ai_response.split()
            for i, word in enumerate(words):
                chunk = {"content": word + (" " if i < len(words) - 1 else ""), "done": False}
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.05)
            
            serializable_state = {
                "messages": [{"type": m.type, "content": m.content} for m in result["messages"]],
                "user_data": result["user_data"],
                "next_step": result.get("next_step", "nama"),
                "session_id": session_id,
                "is_returning_user": is_returning,
                "fortune_full": result.get("fortune_full", ""),
                "interactive_options": result.get("interactive_options")
            }
            
            final_chunk = {
                "content": "",
                "done": True,
                "user_data": result["user_data"],
                "is_complete": is_complete,
                "session_state": serializable_state,
                "session_id": session_id,
                "interactive_options": result.get("interactive_options"),
                "fortune_full": result.get("fortune_full", "")
            }
            yield f"data: {json.dumps(final_chunk)}\n\n"
        
        except Exception as e:
            error_chunk = {"error": str(e), "done": True}
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/reset")
async def reset(request: StartRequest):
    delete_user_data(request.session_id)
    return {
        "session_id": request.session_id,
        "message": "Session reset"
    }
