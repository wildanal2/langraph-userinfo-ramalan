from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel, Field
from src.state import AgentState
from src.config import settings

llm = ChatBedrock(
    model_id=settings.bedrock_model_id,
    region_name=settings.aws_region,
    credentials_profile_name=None,
)

class ExtractedData(BaseModel):
    name: str | None = Field(None, description="Nama user jika disebutkan")
    location: str | None = Field(None, description="Lokasi/kota user jika disebutkan")
    dob: str | None = Field(None, description="Tanggal lahir user jika disebutkan")
    job_field: str | None = Field(None, description="Bidang pekerjaan/profesi user jika disebutkan")
    email: str | None = Field(None, description="Alamat email user jika disebutkan")

structured_llm = llm.with_structured_output(ExtractedData)

COLLECTOR_SYSTEM_PROMPT = """
    Kamu adalah AI Peramal Masa Depan - seorang peramal futuristik yang menggunakan AI untuk memprediksi masa depan karir di industri kreatif.
    Misi: Kumpulkan 5 informasi untuk meramal masa depan mereka:
    1. name - Nama lengkap untuk analisis takdir
    2. location - Kota/lokasi untuk melihat peluang regional
    3. dob - Tanggal lahir untuk analisis pola karir (format: YYYY-MM-DD atau DD/MM/YYYY)
    4. job_field - Bidang kreatif saat ini atau yang diminati (desainer, content creator, animator, dll.)
    5. email - Email untuk mengirim ramalan lengkap
    
    ATURAN PERAMAL AI:
    - Tanya HANYA SATU informasi dalam satu waktu
    - Gunakan bahasa futuristik, menarik, dan persuasif
    - Hubungkan pertanyaan dengan "meramal masa depan" dan "industri kreatif"
    - Jaga respons SINGKAT (maksimal 2-3 kalimat)
    - SELALU gunakan Bahasa Indonesia
    
    CONTOH PERTANYAAN BERDASARKAN FIELD:
    
    name: "Untuk memulai ramalan masa depanmu di industri kreatif, siapa nama lengkapmu?"
    
    location: "Di kota mana kamu berada sekarang? Ini penting untuk melihat peluang industri kreatif di sekitarmu."
    
    dob: "Kapan tanggal lahirmu? (format: DD/MM/YYYY atau YYYY-MM-DD) - Ini akan membantu AI menganalisis pola karirmu."
    
    job_field: "Bidang kreatif apa yang kamu geluti atau minati? (contoh: desainer grafis, content creator, animator, fotografer, dll.)"
    
    email: "Berikan emailmu untuk menerima ramalan lengkap tentang masa depan karirmu di industri kreatif."
    
    Field yang sedang ditanyakan: {next_step}
    
    Bersikaplah futuristik, menarik, dan profesional.
    """

def chatbot_node(state: AgentState) -> AgentState:
    user_data = state["user_data"]
    fields = ["name", "location", "dob", "job_field", "email"]
    
    # Extract data from last user message if it's not the first greeting
    if len(state["messages"]) > 1 and isinstance(state["messages"][-1], HumanMessage):
        extraction_prompt = f"Ekstrak informasi pribadi dari pesan ini: {state['messages'][-1].content}"
        extracted = structured_llm.invoke(extraction_prompt)
        
        # Update user_data with extracted info
        for key in fields:
            if getattr(extracted, key) and not user_data.get(key):
                user_data[key] = getattr(extracted, key)
    
    # Determine next missing field
    next_step = next((f for f in fields if not user_data.get(f)), "complete")
    
    if next_step == "complete":
        return {**state, "user_data": user_data, "next_step": next_step}
    
    # Generate mystical prompt for next field
    system_prompt = COLLECTOR_SYSTEM_PROMPT.format(next_step=next_step)
    context = "Yang sudah kamu tahu: " + ", ".join([f"{k}: {v}" for k, v in user_data.items() if v]) if any(user_data.values()) else "Belum ada"
    
    last_user_msg = next((msg.content for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)), "Halo")
    
    prompt = f"{system_prompt}\n\n{context}\n\nUser berkata: {last_user_msg}\n\nRespond secara mistis dalam Bahasa Indonesia:"
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=response.content)],
        "user_data": user_data,
        "next_step": next_step
    }

def fortune_teller_node(state: AgentState) -> AgentState:
    user_data = state["user_data"]
    
    fortune_prompt = f"""
        Sebagai AI Peramal Masa Depan, buatkan "Ramalan Karir Kreatif" yang SINGKAT, menginspirasi, dan futuristik untuk:
        Nama: {user_data['name']}
        Lokasi: {user_data['location']}
        Tanggal Lahir: {user_data['dob']}
        Bidang Kreatif: {user_data['job_field']}
        
        Buatlah ramalan masa depan:
        - Maksimal 3-4 kalimat
        - Fokus pada peluang dan tren industri kreatif 2-3 tahun ke depan
        - Spesifik untuk bidang kreatif mereka
        - Gunakan bahasa futuristik dan data-driven
        - GUNAKAN BAHASA INDONESIA
        
        Kemudian tambahkan teks INI PERSIS di akhir:
        
        ---
        🚀 Untuk mendapatkan akses penuh ke platform pengembangan karir kreatif dan mewujudkan ramalan ini, daftar sekarang:
        
        👉 [DAFTAR SEKARANG]({settings.sso_register_url}?email={user_data['email']})
        
        Masa depan karirmu menunggu...
    """
    
    response = llm.invoke([HumanMessage(content=fortune_prompt)])
    
    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=response.content)],
        "next_step": "complete"
    }
