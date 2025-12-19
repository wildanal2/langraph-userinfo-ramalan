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

# --- Schema Definition ---
class ExtractedData(BaseModel):
    """Schema untuk ekstraksi data user dari percakapan."""
    nama: str | None = Field(None, description="Nama lengkap user")
    kota: str | None = Field(None, description="Kota domisili user")
    tanggal_lahir: str | None = Field(None, description="Tanggal lahir user")
    bidang_ekraf: str | None = Field(None, description="Bidang ekonomi kreatif yang ditekuni")
    jumlah_komunitas_ekraf_disekitar: str | None = Field(None, description="Jumlah angka komunitas")
    email: str | None = Field(None, description="Alamat email valid")
    no_telepon: str | None = Field(None, description="Nomor telepon")
    harapan: str | None = Field(None, description="Harapan atau tujuan user")

structured_llm = llm.with_structured_output(ExtractedData)

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
    All user data has been collected: {user_data}.
    Generate a thank you message in Indonesian, confirming their data is saved, 
    and tell them they can now start asking questions about creative economy.
    Strict rules: No markdown.
"""


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

    # --- 2. Determine Next Step ---
    # Cari field pertama yang masih kosong (None/Empty String)
    next_step = next((f for f in mandatory_fields if not user_data.get(f)), None)

    # Jika mandatory lengkap, cek optional (bisa di-skip jika ingin mandatory saja cukup)
    # Disini kita asumsi kejar mandatory dulu, lalu optional.
    if not next_step:
        next_step = next((f for f in optional_fields if not user_data.get(f)), "complete")

    if next_step == "complete":
        final_prompt = COMPLETION_PROMPT.format(user_data=str(user_data))
        response = llm.invoke([HumanMessage(content=final_prompt)])

        return {
            "messages": messages + [AIMessage(content=response.content)],
            "user_data": user_data,
            "next_step": "complete",
            "session_id": state["session_id"],
            "is_returning_user": state["is_returning_user"]
        }

    # Generate pertanyaan untuk field selanjutnya
    # Format data agar prompt lebih rapi
    formatted_data = ", ".join([f"{k}: {v}" for k, v in user_data.items() if v])
    prompt_text = COLLECTOR_SYSTEM_PROMPT.format(
        user_data=formatted_data if formatted_data else "None",
        next_step=next_step
    )

    # Gunakan SystemMessage untuk instruksi, HumanMessage untuk trigger
    # Atau gabung di HumanMessage jika model lebih prefer single turn
    response = llm.invoke([HumanMessage(content=prompt_text)])

    return {
        "messages": messages + [AIMessage(content=response.content)],
        "user_data": user_data,
        "next_step": next_step,
        "session_id": state["session_id"],
        "is_returning_user": state["is_returning_user"]
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
        "is_returning_user": state["is_returning_user"]
    }
