import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
    N8N_GET_HISTORY_URL = os.getenv("N8N_GET_HISTORY_URL")
    N8N_GET_SESSIONS_URL = os.getenv("N8N_GET_SESSIONS_URL")  # For sidebar history
    N8N_API_KEY = os.getenv("N8N_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    APP_TITLE = os.getenv("APP_TITLE", "🗨️ Japan Anime-Manga Bot")
    APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "Multi-agent AI")

    @classmethod
    def validate(cls) -> bool:
        required_keys = ["N8N_WEBHOOK_URL", "SUPABASE_URL", "SUPABASE_ANON_KEY"]
        missing = [key for key in required_keys if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        return True
