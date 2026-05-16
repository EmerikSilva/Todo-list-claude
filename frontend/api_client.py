import requests
import streamlit as st

API_BASE_URL = "http://localhost:8000"

def get_headers():
    if 'token' in st.session_state and st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

def _handle_error(response, context=""):
    if response.status_code == 401:
        st.error("Sesión expirada. Por favor, cierra sesión e inicia de nuevo.")
    elif response.status_code == 403:
        st.error("No tienes permiso para realizar esta acción.")
    elif response.status_code == 404:
        st.error(f"Recurso no encontrado. {context}")
    elif response.status_code >= 500:
        st.error(f"Error interno del servidor ({response.status_code}). Revisa que el backend esté corriendo correctamente.")
    else:
        detail = response.json().get("detail", "") if response.headers.get("content-type", "").startswith("application/json") else ""
        st.error(f"Error inesperado ({response.status_code}). {detail}")

def _handle_connection_error():
    st.error("No se puede conectar al backend. Asegúrate de que está corriendo en http://localhost:8000")

def login_user(email, password):
    try:
        response = requests.post(f"{API_BASE_URL}/login", json={"email": email, "password": password})
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.user_email = email
            st.session_state.authenticated = True
            return True, "Login successful!"
        return False, "Credenciales incorrectas."
    except requests.exceptions.ConnectionError:
        return False, "No se puede conectar al backend. Asegúrate de que está corriendo en http://localhost:8000"
    except requests.exceptions.RequestException as e:
        return False, f"Error de conexión: {e}"

def register_user(name, email, password):
    try:
        response = requests.post(f"{API_BASE_URL}/register", json={"name": name, "email": email, "password": password})
        if response.status_code == 200:
            return True, "Registro exitoso. Por favor inicia sesión."
        error_data = response.json()
        return False, error_data.get("detail", "Error al registrar.")
    except requests.exceptions.ConnectionError:
        return False, "No se puede conectar al backend."
    except requests.exceptions.RequestException as e:
        return False, f"Error de conexión: {e}"

def get_todos():
    try:
        response = requests.get(f"{API_BASE_URL}/todos", headers=get_headers())
        if response.status_code == 200:
            return response.json()
        _handle_error(response, "No se pudieron cargar las tareas.")
        return []
    except requests.exceptions.ConnectionError:
        _handle_connection_error()
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión: {e}")
        return []

def create_todo(title, description="", estimated_hours=None):
    try:
        response = requests.post(
            f"{API_BASE_URL}/todos",
            json={"title": title, "description": description, "completed": False, "estimated_hours": estimated_hours},
            headers=get_headers()
        )
        if response.status_code == 200:
            return True
        _handle_error(response, "No se pudo crear la tarea.")
        return False
    except requests.exceptions.ConnectionError:
        _handle_connection_error()
        return False
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión: {e}")
        return False

def update_todo(todo_id, title, description, completed, estimated_hours=None):
    try:
        response = requests.put(
            f"{API_BASE_URL}/todos/{todo_id}",
            json={"title": title, "description": description, "completed": completed, "estimated_hours": estimated_hours},
            headers=get_headers()
        )
        if response.status_code == 200:
            return True
        _handle_error(response, "No se pudo actualizar la tarea.")
        return False
    except requests.exceptions.ConnectionError:
        _handle_connection_error()
        return False
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión: {e}")
        return False

def delete_todo(todo_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/todos/{todo_id}", headers=get_headers())
        if response.status_code == 200:
            return True
        _handle_error(response, "No se pudo eliminar la tarea.")
        return False
    except requests.exceptions.ConnectionError:
        _handle_connection_error()
        return False
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión: {e}")
        return False

def add_time_log(todo_id, duration_seconds, note=""):
    try:
        response = requests.post(
            f"{API_BASE_URL}/todos/{todo_id}/time-log",
            json={"duration_seconds": duration_seconds, "note": note},
            headers=get_headers()
        )
        if response.status_code == 200:
            return True
        _handle_error(response, "No se pudo guardar el tiempo.")
        return False
    except requests.exceptions.ConnectionError:
        _handle_connection_error()
        return False
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión: {e}")
        return False

def get_user_profile():
    try:
        response = requests.get(f"{API_BASE_URL}/profile", headers=get_headers())
        if response.status_code == 200:
            return response.json()
        _handle_error(response, "No se pudo cargar el perfil.")
        return None
    except requests.exceptions.ConnectionError:
        _handle_connection_error()
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión: {e}")
        return None
