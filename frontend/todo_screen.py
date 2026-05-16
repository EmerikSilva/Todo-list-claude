import streamlit as st
from api_client import get_todos, create_todo, update_todo, delete_todo, get_user_profile

def todo_list_screen():
    st.title("📝 My Todo List")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        profile_data = get_user_profile()
        display_name = profile_data['name'] if profile_data else st.session_state.user_email
        st.write(f"Welcome, {display_name}!")
    with col2:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.token = None
            st.session_state.user_email = None
            st.rerun()
    
    st.divider()
    
    with st.form("add_todo_form"):
        st.subheader("Add New Todo")
        new_title = st.text_input("Title")
        new_description = st.text_area("Description (optional)")
        add_button = st.form_submit_button("Add Todo")
        
        if add_button:
            if new_title:
                if create_todo(new_title, new_description):
                    st.success("Todo added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add todo")
            else:
                st.error("Please enter a title")
    
    st.divider()
    
    todos = get_todos()
    
    if todos:
        st.subheader("Your Todos")
        
        for todo in todos:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    if todo["completed"]:
                        st.write(f"✅ ~~{todo['title']}~~")
                    else:
                        st.write(f"📌 {todo['title']}")
                    
                    if todo["description"]:
                        st.write(f"   *{todo['description']}*")
                
                with col2:
                    status = "Completed" if todo["completed"] else "Pending"
                    st.write(status)
                
                with col3:
                    toggle_status = st.button(
                        "Mark Pending" if todo["completed"] else "Mark Complete",
                        key=f"toggle_{todo['id']}"
                    )
                    if toggle_status:
                        if update_todo(todo["id"], todo["title"], todo["description"], not todo["completed"]):
                            st.success("Todo updated!")
                            st.rerun()
                        else:
                            st.error("Failed to update todo")
                
                with col4:
                    if st.button("Delete", key=f"delete_{todo['id']}"):
                        if delete_todo(todo["id"]):
                            st.success("Todo deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete todo")
                
                st.divider()
    else:
        st.info("No todos yet. Add your first todo above!")