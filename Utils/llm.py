from langchain_google_genai import ChatGoogleGenerativeAI

from config import settings

gemini_llm = ChatGoogleGenerativeAI(
    model = "models/gemini-2.0-flash",
    temperature = 0.3,
    google_api_key = settings.google_api_key
)

