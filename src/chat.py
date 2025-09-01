import requests
from datetime import datetime
from .config import Config
from .database import Database


class ChatManager:
    def __init__(self) -> None:
        self.db = Database()

    def send_message(self, message: str, session_id: str | None, user=None) -> str:
        payload = {
            "message": message,
            "session_id": session_id,
            "source": "streamlit",
            "timestamp": datetime.now().isoformat(),
        }
        print(f"[send_message] payload: {payload}")
        if user:
            payload["user_id"] = getattr(user, "id", None)
            payload["username"] = getattr(user, "email", None)

        headers = {}
        if Config.N8N_API_KEY:
            headers["X-API-Key"] = Config.N8N_API_KEY

        try:
            print(f"[send_message] POST {Config.N8N_WEBHOOK_URL} headers: {headers}")
            resp = requests.post(Config.N8N_WEBHOOK_URL, json=payload, headers=headers, timeout=90)
            print(f"[send_message] Response status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"[send_message] Response JSON: {data}")
                if isinstance(data, dict):
                    return data
                return {"response": "Processing completed"}
            print(f"[send_message] Request failed: {resp.status_code}")
            return {"response": f"Request failed: {resp.status_code}"}

        except requests.exceptions.Timeout:
            print("[send_message] Request timeout")
            return {"response": "Request timeout, please try again"}
        except Exception as exc:  # noqa: BLE001
            print(f"[send_message] Connection error: {exc}")
            return {"response": f"Connection error: {exc}"}

    def get_history(self, username: str | None = None, session_id: str | None = None) -> list:
        payload: dict = {"source": "streamlit"}
        if username:
            payload["username"] = username
        if session_id:
            payload["session_id"] = session_id

        print(f"[get_history] payload: {payload}")
        headers = {}
        if Config.N8N_API_KEY:
            headers["X-API-Key"] = Config.N8N_API_KEY

        if not Config.N8N_GET_HISTORY_URL:
            print("[get_history] N8N_GET_HISTORY_URL not configured")
            return []

        print(f"[get_history] POST {Config.N8N_GET_HISTORY_URL} headers: {headers}")
        try:
            resp = requests.post(Config.N8N_GET_HISTORY_URL, json=payload, headers=headers, timeout=30)
            print(f"[get_history] Response status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"[get_history] Response JSON: {data}")
                if isinstance(data, list) and data and "messages" in data[0]:
                    messages = data[0].get("messages", [])
                    return messages
                elif isinstance(data, dict) and "messages" in data:
                    messages = data.get("messages", [])
                    return messages
                else:
                    print("[get_history] Unexpected data format")
                    return []
            else:
                print(f"[get_history] HTTP error: {resp.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"[get_history] RequestException: {e}")
            return []
        except Exception as e:
            print(f"[get_history] Exception: {e}")
            return []

    def get_session_list(self, username: str) -> list:
        """Fetches the list of chat sessions for a user."""
        if not Config.N8N_GET_SESSIONS_URL:
            print("[get_session_list] N8N_GET_SESSIONS_URL not configured")
            return []
        url = f"{Config.N8N_GET_SESSIONS_URL}?username={username}"
        print(f"[get_session_list] url: {url}")
        headers = {}
        if Config.N8N_API_KEY:
            headers["X-API-Key"] = Config.N8N_API_KEY

        print(f"[get_session_list] headers: {headers}")
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            print(f"[get_session_list] Response status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"[get_session_list] Response JSON: {data}")
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and 'sessions' in data[0]:
                    sessions = data[0]['sessions']
                    return sessions
                elif isinstance(data, list):
                    return data
                else:
                    print("[get_session_list] Unexpected data format")
                    return []
            else:
                print(f"[get_session_list] HTTP error: {resp.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"[get_session_list] RequestException: {e}")
            return []
        except Exception as e:
            print(f"[get_session_list] Exception: {e}")
            return []
