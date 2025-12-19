from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
from src.models.schemas import StartRequest, ChatRequest
from src.services import LLMService, SessionService, PromptService
from src.graph import graph
from src.core.logging import get_logger
from src.api.dependencies import verify_content_length
import json
import asyncio
import uuid

logger = get_logger(__name__)
router = APIRouter(tags=["chat"])

llm_service = LLMService()
session_service = SessionService()

@router.post("/start-message", dependencies=[Depends(verify_content_length)])
async def start_message(request: StartRequest):
    async def generate():
        try:
            session_id = request.session_id or str(uuid.uuid4())
            user_data = session_service.get_user_data(session_id)
            
            if user_data:
                prompt = PromptService.format_welcome_returning(user_data.get('nama', 'User'))
            else:
                prompt = PromptService.WELCOME_NEW_USER
            
            for chunk in llm_service.stream(prompt):
                yield f"data: {json.dumps({'content': chunk.content, 'done': False})}\n\n"
                await asyncio.sleep(0.01)
            
            interactive_options = None
            if user_data and user_data.get("nama"):
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
            logger.error(f"Start message error: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@router.post("/chat/stream", dependencies=[Depends(verify_content_length)])
async def chat_stream(request: ChatRequest):
    async def generate():
        try:
            session_id = request.session_id or str(uuid.uuid4())
            user_data = session_service.get_user_data(session_id)
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
            logger.error(f"Chat stream error: {e}", exc_info=True)
            error_chunk = {"error": str(e), "done": True}
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@router.post("/reset")
async def reset_session(request: StartRequest):
    try:
        if request.session_id:
            session_service.delete_session(request.session_id)
        return {
            "session_id": request.session_id,
            "message": "Session reset successfully"
        }
    except Exception as e:
        logger.error(f"Reset session error: {e}", exc_info=True)
        return {
            "session_id": request.session_id,
            "message": "Session reset failed",
            "error": str(e)
        }
