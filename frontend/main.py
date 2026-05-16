import streamlit as st
from auth_screen import login_register_screen
from todo_screen import todo_list_screen
from profile_screen import profile_screen

st.set_page_config(
    page_title="Todo List App",
    page_icon="📝",
    layout="wide"
)

def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None

def main():
    init_session_state()
    
    if not st.session_state.authenticated:
        login_register_screen()
    else:
        page = st.sidebar.selectbox(
            "Navigation",
            ["Todo List", "Profile"]
        )
        
        if page == "Todo List":
            todo_list_screen()
        elif page == "Profile":
            profile_screen()

if __name__ == "__main__":
    main()