from langchain_core.messages import HumanMessage, AIMessage
from src.models.state import AgentState
from src.services import LLMService, SessionService, PromptService
from src.core.config import settings
from src.core.logging import get_logger
from src.core.security import validate_email, validate_phone, validate_date

logger = get_logger(__name__)

llm_service = LLMService()
session_service = SessionService()

BIDANG_EKRAF_OPTIONS = [
    "Aplikasi", "Arsitektur", "Desain Interior", "Desain Komunikasi Visual (DKV)",
    "Desain Produk", "Fashion", "Film, Animasi, dan Video", "Fotografi",
    "Kriya (kerajinan)", "Kuliner", "Musik", "Penerbitan", "Periklanan",
    "Seni Pertunjukan", "Seni Rupa", "Televisi dan Radio", "Permainan Interaktif (Game Developer)"
]

KOMUNITAS_OPTIONS = ["Ada 1", "Ada banyak >2"]

def chatbot_node(state: AgentState) -> AgentState:
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
        extracted = llm_service.extract_data(extraction_prompt)

        for key in all_fields:
            extracted_val = getattr(extracted, key)
            if extracted_val and not user_data.get(key):
                # Validate specific fields (except tanggal_lahir - let LLM handle it)
                if key == "email" and not validate_email(extracted_val):
                    validation_failed = (key, user_input)
                    break
                if key == "no_telepon" and not validate_phone(extracted_val):
                    validation_failed = (key, user_input)
                    break
                user_data[key] = extracted_val
        
        session_service.save_user_data(session_id, user_data)
    
    # Handle validation error with friendly message
    if validation_failed:
        field_name, invalid_input = validation_failed
        user_name = user_data.get("nama", "")
        error_prompt = PromptService.format_validation_error(user_name, invalid_input, field_name)
        response_content = llm_service.invoke(error_prompt)
        
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

    next_step = next((f for f in mandatory_fields if not user_data.get(f)), None)
    if not next_step:
        next_step = next((f for f in optional_fields if not user_data.get(f)), "complete")

    if next_step == "complete":
        user_msg = messages[-1].content.lower() if messages and isinstance(messages[-1], HumanMessage) else ""
        
        if "ramalan karir" in user_msg:
            prompt = PromptService.format_completion_prompt(
                user_data.get("nama", ""),
                user_data.get("kota", ""),
                user_data.get("tanggal_lahir", "")
            )
            response_content = llm_service.invoke(prompt)
            
            return {
                "messages": messages + [AIMessage(content=response_content)],
                "user_data": user_data,
                "next_step": "complete",
                "session_id": session_id,
                "is_returning_user": state["is_returning_user"],
                "intent": state.get("intent", "answering"),
                "fortune_full": response_content,
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
    response_content = llm_service.invoke(prompt)

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

def classifier_node(state: AgentState) -> AgentState:
    messages = state.get("messages", [])
    user_msg = messages[-1].content if messages else ""
    
    if "ramalan karir" in user_msg.lower():
        return {
            **state,
            "intent": "answering"
        }
    
    last_ai_msg = next((m.content for m in reversed(messages[:-1]) if isinstance(m, AIMessage)), None)
    prompt = PromptService.format_intent_prompt(last_ai_msg, user_msg)
    intent = llm_service.classify_intent(prompt)
    
    return {
        **state,
        "intent": intent
    }

def rag_node(state: AgentState) -> AgentState:
    messages = state.get("messages", [])
    user_msg = messages[-1].content if messages else ""
    user_name = state["user_data"].get("nama", "User")

    prompt = PromptService.format_rag_prompt(user_name, user_msg)
    response_content = llm_service.invoke(prompt)

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
