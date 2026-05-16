import streamlit as st
from api_client import login_user, register_user

def login_register_screen():
    st.markdown("""
    <div style="text-align:center; padding:2rem 0 1.5rem;">
        <div style="font-size:3rem; margin-bottom:0.5rem;">⚡</div>
        <h1 style="margin:0; font-size:2.4rem; font-weight:800;
                   background:linear-gradient(135deg,#6366f1,#8b5cf6,#ec4899);
                   -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                   background-clip:text;">
            TaskFlow
        </h1>
        <p style="color:var(--c-text2); font-size:1rem; margin-top:8px;">
            Organiza tu tiempo. Mide tu progreso. Logra más.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        tab1, tab2 = st.tabs(["Iniciar sesión", "Crear cuenta"])

        with tab1:
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            with st.form("login_form"):
                email = st.text_input("📧 Email")
                password = st.text_input("🔒 Contraseña", type="password")
                submitted = st.form_submit_button("Entrar →")
                if submitted:
                    if email and password:
                        success, message = login_user(email, password)
                        if success:
                            st.success("¡Bienvenido!")
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.warning("Por favor completa todos los campos.")

        with tab2:
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            with st.form("register_form"):
                reg_name = st.text_input("👤 Nombre")
                reg_email = st.text_input("📧 Email", key="reg_email")
                reg_password = st.text_input("🔒 Contraseña", type="password", key="reg_pass")
                reg_confirm = st.text_input("🔒 Confirmar contraseña", type="password")
                submitted = st.form_submit_button("Crear cuenta →")
                if submitted:
                    if reg_name and reg_email and reg_password and reg_confirm:
                        if len(reg_password) < 5:
                            st.error("La contraseña debe tener al menos 5 caracteres.")
                        elif reg_password != reg_confirm:
                            st.error("Las contraseñas no coinciden.")
                        else:
                            success, message = register_user(reg_name, reg_email, reg_password)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
                    else:
                        st.warning("Por favor completa todos los campos.")
