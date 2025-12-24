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
    async def generate():
        session_id = request.session_id or str(uuid.uuid4())
        with langwatch.trace(name="start_message") as trace:

            trace.update(input=session_id)

            try:
                user_data = session_service.get_user_data(session_id)
                if user_data:
                    prompt = PromptService.format_welcome_returning(user_data.get('nama', 'User'))
                else:
                    prompt = PromptService.WELCOME_NEW_USER
                full_response = ""
                async for chunk in llm_service.astream(prompt):
                    content = ""
                    if isinstance(chunk.content, str):
                        content = chunk.content
                    elif isinstance(chunk.content, list):
                        for item in chunk.content:
                            if isinstance(item, dict) and 'text' in item:
                                content += item['text']
                    if content:
                        full_response += content
                        yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"
                        await asyncio.sleep(0.02)

                trace.update(output=full_response)

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
                trace.update(error=str(e))
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@router.post("/chat/stream", dependencies=[Depends(verify_content_length)])
async def chat_stream(request: ChatRequest):
    async def generate():
        session_id = request.session_id or str(uuid.uuid4())
        with langwatch.trace(name="chat_stream") as trace:
            try:
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

                trace.update(input=request.message)
                
                full_response = ""
                final_state = None
                async for chunk in graph.astream(state, stream_mode="values"):
                    final_state = chunk
                    current_messages = chunk.get("messages", [])
                    if current_messages:
                        last_message = current_messages[-1]
                        if isinstance(last_message, AIMessage):
                            content = last_message.content
                            if isinstance(content, list):
                                text_content = ""
                                for item in content:
                                    if isinstance(item, dict) and 'text' in item:
                                        text_content += item['text']
                                    elif isinstance(item, str):
                                        text_content += item
                                content = text_content
                            if content and content != full_response:
                                new_content = content[len(full_response):]
                                full_response = content
                                words = new_content.split()
                                for i, word in enumerate(words):
                                    word_chunk = word + (" " if i < len(words) - 1 else "")
                                    chunk_data = {
                                        "content": word_chunk,
                                        "done": False
                                    }
                                    yield f"data: {json.dumps(chunk_data)}\n\n"
                                    await asyncio.sleep(0.02)
                
                if final_state is None:
                    final_state = state
                    final_state["messages"].append(AIMessage(content=full_response or "..."))
                
                trace.update(output=full_response)

                is_complete = final_state.get("next_step") == "complete"
                serializable_state = {
                    "messages": [
                        {"type": m.type, "content": m.content} 
                        for m in final_state.get("messages", [])
                    ],
                    "user_data": final_state.get("user_data", {}),
                    "next_step": final_state.get("next_step", "nama"),
                    "session_id": session_id,
                    "is_returning_user": is_returning,
                    "fortune_full": final_state.get("fortune_full", ""),
                    "interactive_options": final_state.get("interactive_options")
                }
                
                final_chunk = {
                    "content": "",
                    "done": True,
                    "user_data": final_state.get("user_data", {}),
                    "is_complete": is_complete,
                    "session_state": serializable_state,
                    "session_id": session_id,
                    "interactive_options": final_state.get("interactive_options"),
                    "fortune_full": final_state.get("fortune_full", "")
                }
                yield f"data: {json.dumps(final_chunk)}\n\n"
                
            except Exception as e:
                logger.error(f"Chat stream error: {e}", exc_info=True)
                trace.update(error=str(e))
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
