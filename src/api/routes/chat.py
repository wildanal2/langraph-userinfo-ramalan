from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
import langwatch
from src.models.schemas import StartRequest, ChatRequest
from src.services import LLMService, SessionService, PromptService
from src.graph import graph
from src.core.logging import get_logger
from src.core.config import settings
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
    @langwatch.trace(name="start_message")
    async def traced_start_message(session_id: str, user_data: dict):
        if user_data:
            prompt = PromptService.format_welcome_returning(user_data.get('nama', 'User'))
        else:
            prompt = PromptService.WELCOME_NEW_USER
        
        response_text = ""
        for chunk in llm_service.stream(prompt):
            if isinstance(chunk.content, str):
                response_text += chunk.content
            elif isinstance(chunk.content, list):
                for item in chunk.content:
                    if isinstance(item, dict) and 'text' in item:
                        response_text += item['text']
        
        return {
            "response": response_text,
            "session_id": session_id,
            "is_returning": user_data is not None
        }
    
    async def generate():
        try:
            session_id = request.session_id or str(uuid.uuid4())
            user_data = session_service.get_user_data(session_id)
            
            # Call traced function
            result = await traced_start_message(session_id, user_data or {})
            response_text = result["response"]
            
            # Stream response
            words = response_text.split()
            for i, word in enumerate(words):
                yield f"data: {json.dumps({'content': word + (' ' if i < len(words) - 1 else ''), 'done': False})}\n\n"
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
    @langwatch.trace(name="chat_stream")
    async def traced_chat_stream(message: str, session_id: str, user_data: dict, session_state: dict):
        is_returning = user_data is not None
        
        if session_state:
            state = session_state
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
        
        state["messages"].append(HumanMessage(content=message))
        state["session_id"] = session_id
        state["is_returning_user"] = is_returning
        
        result = graph.invoke(state)
        
        ai_response = result["messages"][-1].content if result["messages"] else "..."
        if isinstance(ai_response, list):
            # Extract text from list of dicts
            text_parts = []
            for item in ai_response:
                if isinstance(item, dict) and 'text' in item:
                    text_parts.append(item['text'])
            ai_response = ''.join(text_parts)
        is_complete = result.get("next_step") == "complete"
        
        return {
            "input": message,
            "output": ai_response,
            "result": result,
            "is_complete": is_complete,
            "session_id": session_id,
            "metadata": {
                "user_id": user_data.get("email") if user_data else session_id,
                "is_returning": is_returning,
                "next_step": result.get("next_step"),
                "collected_fields": list(result["user_data"].keys())
            }
        }
    
    async def generate():
        try:
            session_id = request.session_id or str(uuid.uuid4())
            user_data = session_service.get_user_data(session_id)
            
            # Call traced function
            traced_result = await traced_chat_stream(
                request.message,
                session_id,
                user_data or {},
                request.session_state
            )
            
            ai_response = traced_result["output"]
            result = traced_result["result"]
            is_complete = traced_result["is_complete"]
            
            # Stream response
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
                "is_returning_user": user_data is not None,
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
