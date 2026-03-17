import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # =========================
    # 🔐 API KEYS
    # =========================
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

    # =========================
    # 🧠 MODELS
    # =========================
    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL", "gemini-embedding-001"
    )

    LLM_MODEL = os.getenv(
        "LLM_MODEL", "gemini-2.5-flash"
    )

    # =========================
    # 🗄️ DATABASE
    # =========================
    DATABASE_URL = os.getenv("DATABASE_URL")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # =========================
    # 📦 CHUNKING
    # =========================
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 700))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 120))

    # =========================
    # ⏱️ DATA FRESHNESS
    # =========================
    REFRESH_DAYS = int(os.getenv("REFRESH_DAYS", 7))

    # =========================
    # 📂 LOCAL STORAGE
    # =========================
    DATA_DIR = os.getenv("DATA_DIR", "data")


settings = Settings()
