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
        if user:
            payload["user_id"] = getattr(user, "id", None)
            payload["username"] = getattr(user, "email", None)

        headers = {}
        if Config.N8N_API_KEY:
            headers["X-API-Key"] = Config.N8N_API_KEY

        try:
            resp = requests.post(Config.N8N_WEBHOOK_URL, json=payload, headers=headers, timeout=90)
            if resp.status_code == 200:
                data = resp.json()
                # Return the entire data object, not just the response text
                if isinstance(data, dict):
                    return data
                # If not a dictionary, wrap it in a dictionary to maintain type consistency
                return {"response": "Processing completed"}
            return {"response": f"Request failed: {resp.status_code}"}

        except requests.exceptions.Timeout:
            return {"response": "Request timeout, please try again"}
        except Exception as exc:  # noqa: BLE001
            return {"response": f"Connection error: {exc}"}

    def get_history(self, username: str | None = None, session_id: str | None = None) -> list:
        payload: dict = {"source": "streamlit"}
        if username:
            payload["username"] = username
        if session_id:
            payload["session_id"] = session_id

        headers = {}
        if Config.N8N_API_KEY:
            headers["X-API-Key"] = Config.N8N_API_KEY

        if not Config.N8N_GET_HISTORY_URL:
            print("DEBUG: N8N_GET_HISTORY_URL is not configured")
            return []

        print(f"DEBUG: get_history - payload: {payload}")
        print(f"DEBUG: get_history - URL: {Config.N8N_GET_HISTORY_URL}")
        
        try:
            resp = requests.post(Config.N8N_GET_HISTORY_URL, json=payload, headers=headers, timeout=30)
            print(f"DEBUG: get_history - status code: {resp.status_code}")
            print(f"DEBUG: get_history - response headers: {dict(resp.headers)}")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"DEBUG: get_history - raw response data: {data}")
                print(f"DEBUG: get_history - data type: {type(data)}")
                
                # n8n workflow might return [{"messages": [...]}]
                if isinstance(data, list) and data and "messages" in data[0]:
                    messages = data[0].get("messages", [])
                    print(f"DEBUG: get_history - extracted messages from list format: {messages}")
                    return messages
                elif isinstance(data, dict) and "messages" in data:
                    messages = data.get("messages", [])
                    print(f"DEBUG: get_history - extracted messages from dict format: {messages}")
                    return messages
                else:
                    print(f"DEBUG: get_history - unexpected data format, returning empty list")
                    return []
            else:
                print(f"DEBUG: get_history - HTTP error {resp.status_code}: {resp.text}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching history: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error in get_history: {e}")
            return []

    def get_session_list(self, username: str) -> list:
        """Fetches the list of chat sessions for a user."""
        if not Config.N8N_GET_SESSIONS_URL:
            print("DEBUG: N8N_GET_SESSIONS_URL is not configured")
            return []
        
        # For GET request, we need to pass username as query parameter
        url = f"{Config.N8N_GET_SESSIONS_URL}?username={username}"
        headers = {}
        if Config.N8N_API_KEY:
            headers["X-API-Key"] = Config.N8N_API_KEY

        print(f"DEBUG: get_session_list - username: {username}")
        print(f"DEBUG: get_session_list - URL: {url}")

        try:
            resp = requests.get(url, headers=headers, timeout=30)
            print(f"DEBUG: get_session_list - status code: {resp.status_code}")
            print(f"DEBUG: get_session_list - response headers: {dict(resp.headers)}")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"DEBUG: get_session_list - raw response data: {data}")
                print(f"DEBUG: get_session_list - data type: {type(data)}")
                
                # Handle nested format: [{'sessions': [...]}]
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and 'sessions' in data[0]:
                    sessions = data[0]['sessions']
                    print(f"DEBUG: get_session_list - extracted sessions from nested format: {sessions}")
                    return sessions
                # Handle direct format: [{"session_id": "...", "title": "..."}]
                elif isinstance(data, list):
                    print(f"DEBUG: get_session_list - returning direct format sessions: {data}")
                    return data
                else:
                    print(f"DEBUG: get_session_list - unexpected data format, expected list but got {type(data)}")
                    return []
            else:
                print(f"DEBUG: get_session_list - HTTP error {resp.status_code}: {resp.text}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching session list: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error in get_session_list: {e}")
            return []
