from supabase import create_client, Client
from .config import Config

class Database:
    def __init__(self) -> None:
        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)

