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

BIDANG_EKRAF_OPTIONS = [
    "Aplikasi", "Arsitektur", "Desain Interior", "Desain Komunikasi Visual (DKV)",
    "Desain Produk", "Fashion", "Film, Animasi, dan Video", "Fotografi",
    "Kriya (kerajinan)", "Kuliner", "Musik", "Penerbitan", "Periklanan",
    "Seni Pertunjukan", "Seni Rupa", "Televisi dan Radio", "Permainan Interaktif (Game Developer)"
]

KOMUNITAS_OPTIONS = ["Ada", "Ada, banyak", "Tidak Ada"]

def extract_content(chunk):
    if isinstance(chunk.content, str):
        return chunk.content
    if isinstance(chunk.content, list):
        return "".join([item.get('text', '') for item in chunk.content if isinstance(item, dict)])
    return ""

@router.post("/start-message", dependencies=[Depends(verify_content_length)])
async def start_message(request: StartRequest):
    async def generate():
        session_id = request.session_id or str(uuid.uuid4())

        with langwatch.trace(name="start_message") as trace:
            trace.update(input=session_id)
            try:
                user_data = await session_service.get_user_data(session_id)
                mandatory_fields = ["nama", "kota", "tanggal_lahir"]
                optional_fields = ["bidang_ekraf", "jumlah_komunitas_ekraf_disekitar", "email", "no_telepon"]
                all_fields = mandatory_fields + optional_fields
                next_missing_field = None
                if user_data:
                    next_missing_field = next((f for f in all_fields if not user_data.get(f)), None)
                full_response = ""
                interactive_options = None
                current_step = "complete"
                is_returning_user = False  

                # Ada session_id TAPI data Redis KOSONG (expired)
                if request.session_id and not user_data:
                    is_returning_user = True
                    prompt = PromptService.format_welcome_returning("Sobat Kreatif")
                    async for chunk in llm_service.astream(prompt):
                        content = extract_content(chunk)
                        if content:
                            full_response += content
                            yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"
                    interactive_options = {"type": "fortune_trigger", "text": "🔮 Ramalan Karir"}

                # Ada session_id DAN data Redis Ada TAPI BELUM LENGKAP
                elif user_data and next_missing_field:
                    is_returning_user = True
                    current_step = next_missing_field
                    prompt = PromptService.format_collector_prompt(user_data, next_missing_field)
                    async for chunk in llm_service.astream(prompt):
                        content = extract_content(chunk)
                        if content:
                            full_response += content
                            yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"
                            await asyncio.sleep(0.01)
                    if next_missing_field == "bidang_ekraf":
                        interactive_options = {"type": "quick_reply", "options": BIDANG_EKRAF_OPTIONS}
                    elif next_missing_field == "jumlah_komunitas_ekraf_disekitar":
                        interactive_options = {"type": "quick_reply", "options": KOMUNITAS_OPTIONS}

                # Ada session_id & data Redis lengkap
                elif user_data and not next_missing_field:
                    is_returning_user = True
                    prompt = PromptService.format_welcome_returning(user_data.get('nama', 'User'))
                    async for chunk in llm_service.astream(prompt):
                        content = extract_content(chunk)
                        if content:
                            full_response += content
                            yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"
                    interactive_options = {"type": "fortune_trigger", "text": "🔮 Ramalan Karir"}

                # TIDAK ada session_id = User BARU
                else:
                    is_returning_user = False
                    response_content = PromptService.generate_welcome_new_user()
                    full_response = response_content
                    current_step = "nama"
                    yield f"data: {json.dumps({'content': response_content, 'done': False})}\n\n"

                # Simpan flag is_returning_user ke Redis
                await session_service.set_returning_flag(session_id, is_returning_user)

                trace.update(output=full_response)
                final_payload = {
                    "content": "",
                    "done": True,
                    "session_id": session_id,
                    "is_returning_user": is_returning_user,
                    "user_data": user_data or {},
                    "next_step": current_step,
                    "interactive_options": interactive_options
                }
                yield f"data: {json.dumps(final_payload)}\n\n"

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
                user_data = await session_service.get_user_data(session_id)
                # PRIORITY CHECK untuk is_returning:
                # 1. Dari session_state (jika conversation berlanjut)
                # 2. Dari Redis flag (jika first message setelah /start-message)
                # 3. Dari user_data existence (fallback)
                if request.session_state:
                    is_returning = request.session_state.get("is_returning_user", False)
                else:
                    # First message: cek Redis flag
                    returning_flag = await session_service.get_returning_flag(session_id)
                    if returning_flag is not None:
                        # Ada flag di Redis (dari /start-message)
                        is_returning = returning_flag
                    else:
                        # Fallback: cek user_data
                        is_returning = user_data is not None
                
                if request.session_state:
                    state = request.session_state
                    if state.get("messages") and isinstance(state["messages"][0], dict):
                        state["messages"] = [
                            HumanMessage(content=m["content"]) if m["type"] == "human" 
                            else AIMessage(content=m["content"]) 
                            for m in state["messages"]
                        ]
                    state["user_data"] = user_data or {}
                    state["session_id"] = session_id
                    state["is_returning_user"] = is_returning
                else:
                    if is_returning and user_data is None:
                        next_step = "complete"
                    elif user_data:
                        mandatory_fields = ["nama", "kota", "tanggal_lahir"]
                        optional_fields = ["bidang_ekraf", "jumlah_komunitas_ekraf_disekitar", "email", "no_telepon"]
                        all_fields = mandatory_fields + optional_fields
                        next_missing = next((f for f in all_fields if not user_data.get(f)), None)
                        next_step = next_missing or "complete"
                    else:
                        next_step = "nama"
                    
                    state = {
                        "messages": [],
                        "user_data": user_data or {},
                        "next_step": next_step,
                        "session_id": session_id,
                        "is_returning_user": is_returning,
                        "intent": "answering"
                    }
                
                state["messages"].append(HumanMessage(content=request.message))
                
                # logger.info(f"Chat stream state: is_returning={is_returning}, "
                #            f"user_data_is_none={user_data is None}, "
                #            f"next_step={state.get('next_step')}, "
                #            f"has_session_state={request.session_state is not None}, "
                #            f"returning_flag_from_redis={(await session_service.get_returning_flag(session_id))}")

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
