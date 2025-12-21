from langchain_core.prompts import ChatPromptTemplate
class PromptService:
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
    
    COMPLETION_PROMPT = """
    User data: Nama={nama}, Kota={kota}, Tanggal Lahir={tanggal_lahir}
    
    Generate zodiac and career fortune prediction in Indonesian based on their birth date and city.
    Make it 1 paragraph, max 4 sentences, inspiring and specific to creative economy.
    Strict rules: No markdown, no bold, plain text only.
    """
    
    RAG_SYSTEM_PROMPT = """
    # ROLE
    You are a helpful assistant that answers questions ONLY related to the Indonesian Creative Cities Network (ICCN) and Indonesian Creative Cities Festival (ICCF)
    
    # LIMITATIONS
    1. Base all the answer based on the Context provided
    2. DON'T make answer headline
    3. If the Context DOES NOT provide the answer, please answer "Mohon maaf saat ini informasi yang ditanyakan belum tersedia di database"
    4. Output ONLY plain text. NO markdown, NO bold (**), NO headers (#), NO bullet points (-).
    
    # TONE
    Use engaging Indonesian: friendly, conversational, and approachable, but still polite and professional.

    Context:
    {context}
    """
    
    WELCOME_NEW_USER = """
    Generate a short, friendly welcome message in Indonesian for a new user on a creative economy platform. 
    Ask for their name to get started. 
    Strict rules: Max 3 sentences. Output ONLY the raw text message. Do not use markdown, headers, or quotes.
    """
    
    WELCOME_RETURNING_USER = """
    Generate a short, friendly greeting in Indonesian for a returning user named '{nama}'. 
    Welcome them back to the creative economy platform and ask how you can help. 
    Strict rules: Max 3 sentences. Output ONLY the raw text message. Do not use markdown, headers, or quotes.
    """
    
    INTENT_CLASSIFICATION = """
    Last Bot Message: {last_ai_msg}
    User Message: {user_msg}
    
    Classify intent:
    - 'answering': user responding to bot question
    - 'asking': user asking new question
    """
    
    @staticmethod
    def format_collector_prompt(user_data: dict, next_step: str) -> str:
        formatted_data = ", ".join([f"{k}: {v}" for k, v in user_data.items() if v])
        return PromptService.COLLECTOR_SYSTEM_PROMPT.format(
            user_data=formatted_data if formatted_data else "None",
            next_step=next_step
        )
    
    @staticmethod
    def format_completion_prompt(nama: str, kota: str, tanggal_lahir: str) -> str:
        return PromptService.COMPLETION_PROMPT.format(
            nama=nama, kota=kota, tanggal_lahir=tanggal_lahir
        )
    
    @staticmethod
    def format_rag_prompt():
        return ChatPromptTemplate.from_messages([
            ("system", PromptService.RAG_SYSTEM_PROMPT),
            ("human", "Question : {question}")
        ])
    
    @staticmethod
    def format_welcome_returning(nama: str) -> str:
        return PromptService.WELCOME_RETURNING_USER.format(nama=nama)
    
    @staticmethod
    def format_intent_prompt(last_ai_msg: str, user_msg: str) -> str:
        return PromptService.INTENT_CLASSIFICATION.format(
            last_ai_msg=last_ai_msg or "None", user_msg=user_msg
        )
