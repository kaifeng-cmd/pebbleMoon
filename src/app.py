import streamlit as st
import uuid
from .config import Config
from .auth import Auth, AuthError
from .chat import ChatManager
from .database import Database

Config.validate()

auth = Auth()
chat_manager = ChatManager()
db = Database()


# --- Authentication Page ---
def auth_page() -> None:
    st.title("🔑 Login to your AI Assistant")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login") and email and password:
            try:
                with st.spinner("Logging in..."):
                    resp = auth.sign_in(email, password)
                if getattr(resp, 'user', None):
                    st.session_state.user = resp.user
                    # Update Supabase client session
                    auth.db.client.auth.set_session(resp.session.access_token, resp.session.refresh_token)
                    st.session_state.session_id = None
                    st.session_state.chat_history = []
                    st.session_state.initial_load_done = False
                    st.session_state.page = 'chat'  # Ensure redirect to chat page
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Login failed. Please check your email and password.")
            except AuthError as e:
                st.error(f"Login failed: {str(e)}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

    with tab2:
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")
        confirm = st.text_input("Confirm Password", type="password")
        if st.button("Register") and email and password:
            if password != confirm:
                st.error("Passwords do not match")
            else:
                try:
                    with st.spinner("Checking email availability..."):
                        # First check if email already exists
                        if auth.check_email_exists(email):
                            st.error("This email is already registered. Please use a different email or try logging in.")
                            st.stop()  # Stop further execution
                    
                    with st.spinner("Registering..."):
                        resp = auth.sign_up(email, password)
                    if getattr(resp, 'user', None):
                        st.success("Registration successful! Please check your email to verify your account.")
                    else:
                        st.success("Registration successful! Please check your email to verify your account.")
                except AuthError as e:
                    error_msg = str(e).lower()
                    if "already registered" in error_msg:
                        st.error("This email is already registered. Please use a different email or try logging in.")
                    elif "password" in error_msg:
                        st.error("Password does not meet requirements. Please use a stronger password.")
                    else:
                        st.error(f"Registration failed: {str(e)}")
                except Exception as e:
                    st.error(f"An unexpected error occurred during registration: {str(e)}")


# --- Chat Page ---
def chat_page() -> None:
    CUSTOM_CSS = """
    <style>
        /* 1. Spacing: Target the container of each button for spacing */
        div.stButton {
            margin-bottom: 1px !important;
        }

        /* 2. Button and Text Container Styling */
        div.stButton > button {
            width: 100%;
            justify-content: flex-start !important;
            text-align: left !important;
            position: relative; /* Needed for the gradient overlay */
            padding-right: 20px; /* Space for the fade effect */
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* 3. Smooth Fade Effect for Text Overflow */
        div.stButton > button::after {
            content: '';
            position: absolute;
            right: 0;
            top: 0;
            width: 20px; /* Width of the fade gradient */
            height: 100%;
            background: linear-gradient(to right, transparent, rgba(247, 210, 212, 0.8) 90%, rgba(255, 255, 255, 1));
            pointer-events: none; /* Ensure the gradient doesn't interfere with clicks */
        }

        /* Dark mode adjustment for fade effect */
        [data-theme="dark"] div.stButton > button::after {
            background: linear-gradient(to right, transparent, rgba(17, 17, 17, 0.9) 70%, rgba(17, 17, 17, 1));
        }

        /* 4. Highlighting: Style for the active (primary) session button */
        button[data-testid="baseButton-primary"] {
            background-color: #a8223dff;
            color: white;
            border: 1px solid #a8223dff;
        }
        button[data-testid="baseButton-primary"]:hover {
            background-color: #a8223dff;
            color: white;
            border: 1px solid #a8223dff;
            font-weight: bold;
        }
        button[data-testid="baseButton-primary"]:focus {
            box-shadow: 0 0 0 0.2rem rgba(194, 70, 76, 0.5);
        }

        /* 5. Hover effect for non-active buttons */
        div.stButton > button[kind="secondary"]:hover {
            border-color: #a8223dff !important;
            color: #a8223dff !important;
        }
    </style>
    """
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    st.title(Config.APP_TITLE)
    st.caption(Config.APP_DESCRIPTION)

    with st.sidebar:
        if not st.session_state.user:
            st.info("💡 Login to automatically save and display chat history")
            if st.button("Register or Login"):
                st.session_state.page = 'auth'
                st.rerun()
        
        else:
            st.success(f"🕊️ {getattr(st.session_state.user, 'email', '')}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📝 New Chat", use_container_width=True):
                    st.session_state.session_id = None
                    st.session_state.chat_history = []
                    st.rerun()
            with col2:
                if st.button("🚪 Logout", use_container_width=True):
                    auth.sign_out()
                    st.session_state.user = None
                    st.session_state.session_id = None
                    st.session_state.chat_history = []
                    st.session_state.initial_load_done = False
                    st.rerun()
            
            st.markdown("---")
            st.markdown("#### Chat History")
            
            sessions = chat_manager.get_session_list(getattr(st.session_state.user, 'email', ''))
            if not sessions:
                st.info("No chat history available")
            else:
                sessions.sort(key=lambda x: x.get("session_id", ""), reverse=True)
                for session in sessions:
                    session_title = session.get("title", session.get("session_id", "Chat"))
                    
                    is_active = (session["session_id"] == st.session_state.session_id)
                    button_type = "primary" if is_active else "secondary"
                    
                    if st.button(session_title, key=session["session_id"], use_container_width=True, type=button_type):
                        st.session_state.session_id = session["session_id"]
                        st.session_state.chat_history = chat_manager.get_history(
                            username=getattr(st.session_state.user, 'email', ''),
                            session_id=st.session_state.session_id
                        )
                        st.rerun()

    if st.session_state.user and not st.session_state.initial_load_done:
        sessions = chat_manager.get_session_list(getattr(st.session_state.user, 'email', ''))
        if sessions:
            sessions.sort(key=lambda x: x.get("session_id", ""), reverse=True)
            latest_session_id = sessions[0].get("session_id")
            if latest_session_id:
                st.session_state.session_id = latest_session_id
                st.session_state.chat_history = chat_manager.get_history(
                    username=getattr(st.session_state.user, 'email', ''),
                    session_id=latest_session_id
                )
        st.session_state.initial_load_done = True
        st.rerun()

    for msg in st.session_state.chat_history:
        role = 'user' if msg.get("type") == "human" else 'assistant'
        with st.chat_message(role):
            st.write(msg.get("data", {}).get("content", ""))

    if prompt := st.chat_input("Enter your question..."):
        if not st.session_state.user and not st.session_state.session_id:
            st.session_state.session_id = f"web_anon_{uuid.uuid4().hex}"

        with st.chat_message("user"):
            st.write(prompt)
        
        with st.spinner("🤖 Thinking..."):
            response_data = chat_manager.send_message(prompt, st.session_state.session_id, st.session_state.user)

        ai_text = response_data.get("response", "Sorry, an error occurred while processing.")
        new_session_id = response_data.get("sessionId")

        if new_session_id:
            st.session_state.session_id = new_session_id
        
        with st.chat_message("assistant"):
            st.write(ai_text)
        
        st.session_state.chat_history.append({"type": "human", "data": {"content": prompt}})
        st.session_state.chat_history.append({"type": "ai", "data": {"content": ai_text}})
        
        st.rerun()


# --- Main Application Flow ---
def main() -> None:
    if 'page' not in st.session_state:
        st.session_state.page = 'chat'
    if 'user' not in st.session_state:
        current_user_response = auth.get_current_user()
        st.session_state.user = getattr(current_user_response, 'user', None)
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'initial_load_done' not in st.session_state:
        st.session_state.initial_load_done = False

    if st.session_state.page == 'auth':
        auth_page()
    else:
        chat_page()


def run() -> None:
    main()