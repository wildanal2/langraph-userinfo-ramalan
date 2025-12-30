import asyncio
from langchain_core.messages import HumanMessage, AIMessage
from src.models.state import AgentState
from src.services import LLMService, SessionService, PromptService
from src.services.auth_service import AuthService
from src.rag.retrieval.rag_pipeline import rag_pipeline
from src.core.config import settings
from src.core.logging import get_logger
from src.core.security import validate_phone, validate_date, validate_location, validate_email

logger = get_logger(__name__)

llm_service = LLMService()
session_service = SessionService()
auth_service = AuthService()

def get_rag_chat():
    return rag_pipeline.chat()

BIDANG_EKRAF_OPTIONS = [
    "Aplikasi", "Arsitektur", "Desain Interior", "Desain Komunikasi Visual (DKV)",
    "Desain Produk", "Fashion", "Film, Animasi, dan Video", "Fotografi",
    "Kriya (kerajinan)", "Kuliner", "Musik", "Penerbitan", "Periklanan",
    "Seni Pertunjukan", "Seni Rupa", "Televisi dan Radio", "Permainan Interaktif (Game Developer)"
]

KOMUNITAS_OPTIONS = ["Ada", "Ada, banyak", "Tidak Ada"]

async def chatbot_node(state: AgentState) -> AgentState:
    user_data = state.get("user_data", {})
    messages = state.get("messages", [])
    session_id = state["session_id"]

    mandatory_fields = ["nama", "kota", "tanggal_lahir"]
    optional_fields = ["bidang_ekraf", "jumlah_komunitas_ekraf_disekitar", "email", "no_telepon"]
    all_fields = mandatory_fields + optional_fields

    validation_failed = None
    
    if messages and isinstance(messages[-1], HumanMessage):
        user_input = messages[-1].content
        extraction_prompt = f"Extract user info based on this input: '{user_input}'. Focus on missing fields."
        
        extracted = await llm_service.extract_data(extraction_prompt)

        for key in all_fields:
            extracted_val = getattr(extracted, key)
            if extracted_val and not user_data.get(key):
                if key == "email":
                    extracted_val = extracted_val.strip().lower()
                    
                    is_valid, error_code = validate_email(extracted_val)
                    
                    if not is_valid:
                        if error_code == "typo_detected":
                             validation_failed = (key, user_input, "custom_error", "Format emailnya kurang tepat, tolong input format email dengan benar.")
                        else:
                             validation_failed = (key, user_input, error_code)
                        break
                        
                    is_available, error_msg = await auth_service.check_email(extracted_val)
                    if not is_available:
                        validation_failed = (key, user_input, "custom_error", error_msg)
                        break
                        
                if key == "no_telepon":
                    is_valid, formatted_phone = validate_phone(extracted_val)
                    if not is_valid:
                        validation_failed = (key, user_input, "invalid_format")
                        break
                    extracted_val = formatted_phone

                if key == "tanggal_lahir":
                    is_valid, error_code, formatted_date = validate_date(extracted_val)
                    if not is_valid:
                        validation_failed = (key, user_input, error_code)
                        break
                    extracted_val = formatted_date 
                if key == "kota":
                    is_valid_loc, normalized_loc = validate_location(extracted_val)
                    if not is_valid_loc:
                        validation_failed = (key, user_input, "invalid_location")
                        break
                    extracted_val = normalized_loc
                user_data[key] = extracted_val
        await session_service.save_user_data(session_id, user_data)
    
    # Handle validation error
    if validation_failed:
        if len(validation_failed) == 4:
            field_name, invalid_input, _, custom_msg = validation_failed
            response_content = custom_msg
        else:
            field_name, invalid_input, error_code = validation_failed
            user_name = user_data.get("nama", "")
            error_prompt = PromptService.format_validation_error(
                user_name=user_name,
                invalid_input=invalid_input,
                field_name=field_name,
                error_code=error_code
            )
            response_content = await llm_service.ainvoke(error_prompt)
        
        return {
            "messages": messages + [AIMessage(content=response_content)],
            "user_data": user_data,
            "next_step": field_name,
            "session_id": session_id,
            "is_returning_user": state["is_returning_user"],
            "intent": state.get("intent", "answering"),
            "fortune_full": state.get("fortune_full", ""),
            "interactive_options": None
        }

    # Check if user just completed 4th field for motivation message
    filled_count = len([v for v in user_data.values() if v])
    show_motivation = filled_count == 4

    next_step = next((f for f in mandatory_fields if not user_data.get(f)), None)
    if not next_step:
        next_step = next((f for f in optional_fields if not user_data.get(f)), "complete")

    if next_step == "complete":
        user_msg = messages[-1].content.lower() if messages and isinstance(messages[-1], HumanMessage) else ""
        
        if "ramalan karir" in user_msg:
            fortune_gimmick = (await session_service.get_user_data(session_id)).get("ramalan_gimmick")
            if fortune_gimmick:
                # logger.info("Returning fortune gimmick")
                return {
                    "messages": messages + [AIMessage(content=fortune_gimmick)],
                    "user_data": user_data,
                    "next_step": "complete",
                    "session_id": session_id,
                    "is_returning_user": state["is_returning_user"],
                    "intent": state.get("intent", "answering"),
                    "fortune_full": fortune_gimmick,
                    "interactive_options": {
                        "type": "sso_button", 
                        "text": "✨ Cek Hasil Lengkapnya", 
                        "url": f"{settings.sso_register_url}?session_id={session_id}"
                    }
                }
            else:
                fortune_gimmick_prompt = PromptService.format_gimmick_prompt(
                    user_data.get("nama", ""),
                    user_data.get("kota", ""),
                    user_data.get("tanggal_lahir", "")
                )
                fortune_full_prompt = PromptService.format_full_prompt(
                    user_data.get("nama", ""),
                    user_data.get("kota", ""),
                    user_data.get("tanggal_lahir", "")
                ) 
                # logger.info("Generating new fortune full & gimmick")
                async def generate_fortune_full():
                    fortune_full = await llm_service.ainvoke(fortune_full_prompt)
                    await session_service.save_user_data(session_id, {"ramalan_full": fortune_full})
                    logger.info(f"FINISHED generating Full Fortune for user:{session_id}")
                asyncio.create_task(generate_fortune_full())
                fortune_gimmick = await llm_service.ainvoke(fortune_gimmick_prompt)
                await session_service.save_user_data(session_id, {"ramalan_gimmick": fortune_gimmick})
                return {
                    "messages": messages + [AIMessage(content=fortune_gimmick)],
                    "user_data": user_data,
                    "next_step": "complete",
                    "session_id": session_id,
                    "is_returning_user": state["is_returning_user"],
                    "intent": state.get("intent", "answering"),
                    "fortune_full": fortune_gimmick,
                    "interactive_options": {
                        "type": "sso_button", 
                        "text": "✨ Cek Hasil Lengkapnya", 
                        "url": f"{settings.sso_register_url}?session_id={session_id}"
                    }
                }
        else:
            return {
                "messages": messages + [AIMessage(content="Data kamu sudah lengkap! Klik tombol di bawah untuk melihat ramalan karirmu.")],
                "user_data": user_data,
                "next_step": "complete",
                "session_id": session_id,
                "is_returning_user": state["is_returning_user"],
                "intent": state.get("intent", "answering"),
                "fortune_full": state.get("fortune_full", ""),
                "interactive_options": {"type": "fortune_trigger", "text": "🔮 Ramalan Karir"}
            }

    prompt = PromptService.format_collector_prompt(user_data, next_step)
    response_content = await llm_service.ainvoke(prompt)
    
    # Add motivation separator marker after 4th answer
    if show_motivation:
        response_content = "[SEPARATOR:Dikit lagi untuk lihat hasilnya...]" + response_content

    interactive_options = None
    if next_step == "bidang_ekraf":
        interactive_options = {"type": "quick_reply", "options": BIDANG_EKRAF_OPTIONS}
    elif next_step == "jumlah_komunitas_ekraf_disekitar":
        interactive_options = {"type": "quick_reply", "options": KOMUNITAS_OPTIONS}

    return {
        "messages": messages + [AIMessage(content=response_content)],
        "user_data": user_data,
        "next_step": next_step,
        "session_id": session_id,
        "is_returning_user": state["is_returning_user"],
        "intent": state.get("intent", "answering"),
        "fortune_full": state.get("fortune_full", ""),
        "interactive_options": interactive_options
    }

async def classifier_node(state: AgentState) -> AgentState:
    messages = state.get("messages", [])
    user_msg = messages[-1].content if messages else ""
    
    if "ramalan karir" in user_msg.lower():
        return {
            **state,
            "intent": "answering"
        }
    
    last_ai_msg = next((m.content for m in reversed(messages[:-1]) if isinstance(m, AIMessage)), None)
    prompt = PromptService.format_intent_prompt(last_ai_msg, user_msg)

    intent = await llm_service.classify_intent(prompt)
    
    return {
        **state,
        "intent": intent
    }

async def rag_node(state: AgentState) -> AgentState:
    messages = state.get("messages", [])
    user_msg = messages[-1].content if messages else ""
    rag_chat = await get_rag_chat()
    
    response_content = await rag_chat.ainvoke({"question": user_msg})

    return {
        "messages": messages + [AIMessage(content=response_content)],
        "user_data": state["user_data"],
        "next_step": state["next_step"],
        "session_id": state["session_id"],
        "is_returning_user": state["is_returning_user"],
        "intent": state.get("intent", "asking"),
        "fortune_full": state.get("fortune_full", ""),
        "interactive_options": state.get("interactive_options")
    }