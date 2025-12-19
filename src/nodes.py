from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field
from src.state import AgentState
from src.config import settings
from src.redis_client import save_user_data

llm = ChatBedrock(
    model_id=settings.bedrock_model_id,
    region_name=settings.aws_region,
    credentials_profile_name=None,
)

class ExtractedData(BaseModel):
    nama: str | None = Field(None, description="Nama lengkap user")
    kota: str | None = Field(None, description="Kota domisili user")
    tanggal_lahir: str | None = Field(None, description="Tanggal lahir user")
    bidang_ekraf: str | None = Field(None, description="Bidang ekonomi kreatif yang ditekuni")
    jumlah_komunitas_ekraf_disekitar: str | None = Field(None, description="Jumlah angka komunitas")
    email: str | None = Field(None, description="Alamat email valid")
    no_telepon: str | None = Field(None, description="Nomor telepon")
    harapan: str | None = Field(None, description="Harapan atau tujuan user")

class IntentClassification(BaseModel):
    intent: str = Field(description="'answering' if user is responding to question, 'asking' if user is asking question")

structured_llm = llm.with_structured_output(ExtractedData)
intent_llm = llm.with_structured_output(IntentClassification)

# --- Prompt Improvement ---
# Instruksi dalam Inggris untuk presisi logika, Output diminta Indonesia.
COLLECTOR_SYSTEM_PROMPT = """
    You are a friendly and professional creative economy assistant. 
    Your goal is to collect user information profile step-by-step.
    
    Current Data Collected: {user_data}
    Missing Field to Ask: {next_step}
    
    Instructions:
    1. Ask the user ONLY for the '{next_step}'.
    2. Be polite and friendly. Use casual Indonesian (Bahasa Indonesia).
    3. Do not ask for multiple fields at once.
    4. Keep the question short (max 4 sentences).
    5. Output ONLY the raw text message. Do not use markdown, headers, or quotes or bold.
"""

# Prompt khusus jika semua data sudah lengkap
COMPLETION_PROMPT = """
    User data: Nama={nama}, Kota={kota}, Tanggal Lahir={tanggal_lahir}
    
    Generate zodiac and career fortune prediction in Indonesian based on their birth date and city.
    Make it 1 paragraph, max 4 sentences, inspiring and specific to creative economy.
    Strict rules: No markdown, no bold, plain text only.
"""


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

    if messages and isinstance(messages[-1], HumanMessage):
        extraction_prompt = f"Extract user info based on this input: '{messages[-1].content}'. Focus on missing fields."
        extracted = structured_llm.invoke(extraction_prompt)

        for key in all_fields:
            extracted_val = getattr(extracted, key)
            if extracted_val and not user_data.get(key):
                user_data[key] = extracted_val
        
        save_user_data(session_id, user_data)

    next_step = next((f for f in mandatory_fields if not user_data.get(f)), None)
    if not next_step:
        next_step = next((f for f in optional_fields if not user_data.get(f)), "complete")

    if next_step == "complete":
        user_msg = messages[-1].content.lower() if messages and isinstance(messages[-1], HumanMessage) else ""
        
        if "ramalan karir" in user_msg:
            final_prompt = COMPLETION_PROMPT.format(
                nama=user_data.get("nama", ""),
                kota=user_data.get("kota", ""),
                tanggal_lahir=user_data.get("tanggal_lahir", "")
            )
            response = llm.invoke([HumanMessage(content=final_prompt)])
            
            return {
                "messages": messages + [AIMessage(content=response.content if isinstance(response.content, str) else "")],
                "user_data": user_data,
                "next_step": "complete",
                "session_id": state["session_id"],
                "is_returning_user": state["is_returning_user"],
                "intent": state.get("intent", "answering"),
                "fortune_full": response.content if isinstance(response.content, str) else "",
                "interactive_options": {"type": "sso_button", "text": "✨ Cek Hasil Lengkapnya", "url": f"{settings.sso_register_url}?session_id={session_id}"}
            }
        else:
            return {
                "messages": messages + [AIMessage(content="Data kamu sudah lengkap! Klik tombol di bawah untuk melihat ramalan karirmu.")],
                "user_data": user_data,
                "next_step": "complete",
                "session_id": state["session_id"],
                "is_returning_user": state["is_returning_user"],
                "intent": state.get("intent", "answering"),
                "fortune_full": state.get("fortune_full", ""),
                "interactive_options": {"type": "fortune_trigger", "text": "🔮 Ramalan Karir"}
            }

    formatted_data = ", ".join([f"{k}: {v}" for k, v in user_data.items() if v])
    prompt_text = COLLECTOR_SYSTEM_PROMPT.format(
        user_data=formatted_data if formatted_data else "None",
        next_step=next_step
    )
    response = llm.invoke([HumanMessage(content=prompt_text)])

    interactive_options = None
    if next_step == "bidang_ekraf":
        interactive_options = {"type": "quick_reply", "options": BIDANG_EKRAF_OPTIONS}
    elif next_step == "jumlah_komunitas_ekraf_disekitar":
        interactive_options = {"type": "quick_reply", "options": KOMUNITAS_OPTIONS}

    return {
        "messages": messages + [AIMessage(content=response.content)],
        "user_data": user_data,
        "next_step": next_step,
        "session_id": state["session_id"],
        "is_returning_user": state["is_returning_user"],
        "intent": state.get("intent", "answering"),
        "fortune_full": state.get("fortune_full", ""),
        "interactive_options": interactive_options
    }


RAG_SYSTEM_PROMPT = """
    You are a friendly creative economy assistant for young Indonesian users.
    
    User: {user_name}
    Question: {user_msg}
    
    Instructions:
    1. Answer questions about creative economy (ekonomi kreatif) in Indonesian.
    2. Use casual, friendly tone like talking to a young friend (anak muda).
    3. Keep it conversational and relatable.
    4. Output ONLY plain text. NO markdown, NO bold (**), NO headers (#), NO bullet points (-).
    5. Use simple paragraphs with natural line breaks if needed.
"""

def classifier_node(state: AgentState) -> AgentState:
    messages = state.get("messages", [])
    user_msg = messages[-1].content if messages else ""
    
    if "ramalan karir" in user_msg.lower():
        return {
            "messages": state["messages"],
            "user_data": state["user_data"],
            "next_step": state["next_step"],
            "session_id": state["session_id"],
            "is_returning_user": state["is_returning_user"],
            "intent": "answering",
            "fortune_full": state.get("fortune_full", ""),
            "interactive_options": state.get("interactive_options")
        }
    
    last_ai_msg = next((m.content for m in reversed(messages[:-1]) if isinstance(m, AIMessage)), None)
    
    prompt = f"""Last Bot Message: {last_ai_msg or 'None'}
        User Message: {user_msg}
        
        Classify intent:
        - 'answering': user responding to bot question
        - 'asking': user asking new question
    """
    
    result = intent_llm.invoke(prompt)
    
    return {
        "messages": state["messages"],
        "user_data": state["user_data"],
        "next_step": state["next_step"],
        "session_id": state["session_id"],
        "is_returning_user": state["is_returning_user"],
        "intent": result.intent,
        "fortune_full": state.get("fortune_full", ""),
        "interactive_options": state.get("interactive_options")
    }

def rag_node(state: AgentState) -> AgentState:
    messages = state.get("messages", [])
    user_msg = messages[-1].content if messages else ""
    user_name = state["user_data"].get("nama", "User")

    prompt = RAG_SYSTEM_PROMPT.format(user_name=user_name, user_msg=user_msg)
    response = llm.invoke([HumanMessage(content=prompt)])

    return {
        "messages": messages + [AIMessage(content=response.content)],
        "user_data": state["user_data"],
        "next_step": state["next_step"],
        "session_id": state["session_id"],
        "is_returning_user": state["is_returning_user"],
        "intent": state.get("intent", "asking"),
        "fortune_full": state.get("fortune_full", ""),
        "interactive_options": state.get("interactive_options")
    }
