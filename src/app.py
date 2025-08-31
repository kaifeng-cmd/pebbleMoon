import streamlit as st
import uuid
from .config import Config
from .auth import Auth
from .chat import ChatManager
from .database import Database


Config.validate()

auth = Auth()
chat_manager = ChatManager()
db = Database()


# --- Authentication Page ---
def auth_page() -> None:
    st.title("🔐 Login to your AI Assistant")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login") and email and password:
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

    with tab2:
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")
        confirm = st.text_input("Confirm Password", type="password")
        if st.button("Register") and email and password:
            if password != confirm:
                st.error("Passwords do not match")
            else:
                with st.spinner("Registering..."):
                    resp = auth.sign_up(email, password)
                if getattr(resp, 'user', None):
                    st.success("Registration successful! Please check your email")
                else:
                    st.error("Registration failed")


# --- Chat Page ---
def chat_page() -> None:
    st.title(Config.APP_TITLE)
    st.caption(Config.APP_DESCRIPTION)

    with st.sidebar:
        # --- Login/Register Button for Anonymous Users ---
        if not st.session_state.user:
            st.info("💡 Login to automatically save and display chat history")
            if st.button("Login/Register"):
                st.session_state.page = 'auth'
                st.rerun()
        
        # --- Logged-in User Sidebar ---
        else:  # st.session_state.user is not None
            st.success(f"👋 {getattr(st.session_state.user, 'email', '')}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ New Chat", use_container_width=True):
                    st.session_state.session_id = None
                    st.session_state.chat_history = []
                    st.rerun()
            with col2:
                if st.button("🚪 Logout", use_container_width=True):
                    auth.sign_out()
                    st.session_state.user = None
                    st.session_state.session_id = None
                    st.session_state.chat_history = []
                    st.session_state.initial_load_done = False  # Reset flag
                    st.rerun()
            
            st.markdown("---")
            st.markdown("#### Chat History")
            
            # Add debug button for testing
            if st.button("🔍 Test API Connection", use_container_width=True):
                with st.expander("Debug Information"):
                    st.write("**Testing session list retrieval:**")
                    sessions = chat_manager.get_session_list(getattr(st.session_state.user, 'email', ''))
                    st.json(sessions)
                    
                    if sessions:
                        st.write("**Testing chat history retrieval (first session):**")
                        first_session_id = sessions[0].get("session_id")
                        if first_session_id:
                            history = chat_manager.get_history(
                                username=getattr(st.session_state.user, 'email', ''),
                                session_id=first_session_id
                            )
                            st.json(history)
            
            # Fetch sessions for the logged-in user
            sessions = chat_manager.get_session_list(getattr(st.session_state.user, 'email', ''))
            if not sessions:
                st.info("No chat history available")
            else:
                # Display a button for each session
                for session in sessions:
                    session_title = session.get("title", session.get("session_id", "Chat"))
                    if st.button(session_title, key=session["session_id"], use_container_width=True):
                        st.session_state.session_id = session["session_id"]
                        st.session_state.chat_history = chat_manager.get_history(
                            username=getattr(st.session_state.user, 'email', ''),
                            session_id=st.session_state.session_id
                        )
                        st.rerun()

    # --- Initial Load for Logged-in User (only once) ---
    # If user is logged in, and we haven't loaded history yet, try to load the latest session.
    if st.session_state.user and not st.session_state.initial_load_done:
        sessions = chat_manager.get_session_list(getattr(st.session_state.user, 'email', ''))
        if sessions:
            # Sort sessions by session_id to get the most recent one
            sessions.sort(key=lambda x: x.get("session_id", ""), reverse=True)
            latest_session_id = sessions[0].get("session_id")
            if latest_session_id:
                st.session_state.session_id = latest_session_id
                st.session_state.chat_history = chat_manager.get_history(
                    username=getattr(st.session_state.user, 'email', ''),
                    session_id=latest_session_id
                )
        st.session_state.initial_load_done = True  # Mark as loaded
        st.rerun()  # Rerun to display loaded history


    # --- Display Chat Messages ---
    for msg in st.session_state.chat_history:
        role = 'user' if msg.get("type") == "human" else 'assistant'
        with st.chat_message(role):
            st.write(msg.get("data", {}).get("content", ""))

    # --- Chat Input and Message Sending ---
    if prompt := st.chat_input("Enter your question..."):
        # For anonymous users, generate a temporary session_id if none exists
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
        
        # Append new messages to history (no get_history call here)
        st.session_state.chat_history.append({"type": "human", "data": {"content": prompt}})
        st.session_state.chat_history.append({"type": "ai", "data": {"content": ai_text}})
        
        st.rerun()


# --- Main Application Flow ---
def main() -> None:
    # Ensure all necessary session_state keys exist at the start of main function
    # This prevents AttributeError in some Streamlit rerun scenarios
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

    st.write(f"DEBUG: main() - st.session_state.user: {st.session_state.user}")
    if st.session_state.user:
        st.write(f"DEBUG: main() - st.session_state.user.email: {getattr(st.session_state.user, 'email', 'N/A')}")
    st.write(f"DEBUG: main() - st.session_state.session_id: {st.session_state.session_id}")
    st.write(f"DEBUG: main() - st.session_state.page: {st.session_state.page}")


    # If user is on auth page, show auth page
    if st.session_state.page == 'auth':
        auth_page()
    # Otherwise, show chat page (whether logged in or anonymous)
    else:
        chat_page()


def run() -> None:
    main()
