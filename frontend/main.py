import streamlit as st
import streamlit.components.v1 as components
from auth_screen import login_register_screen
from todo_screen import todo_list_screen
from profile_screen import profile_screen

st.set_page_config(
    page_title="TaskFlow",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

def inject_theme_detector():
    """Detecta el tema real de Streamlit y pone data-theme en el <html>."""
    components.html("""
    <script>
    (function() {
        function detect() {
            try {
                var doc = window.parent.document;
                var app = doc.querySelector('.stApp');
                if (!app) { setTimeout(detect, 300); return; }
                var rgb = window.parent.getComputedStyle(app).backgroundColor;
                var m = rgb.match(/\d+/g);
                if (!m) { setTimeout(detect, 300); return; }
                var brightness = (parseInt(m[0])*299 + parseInt(m[1])*587 + parseInt(m[2])*114) / 1000;
                doc.documentElement.setAttribute('data-theme', brightness < 100 ? 'dark' : 'light');
            } catch(e) {}
        }
        detect();
        setInterval(detect, 1500);
    })();
    </script>
    """, height=0, scrolling=False)

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── Variables de color (modo claro) ── */
    :root {
        --c-card:    #ffffff;
        --c-done:    #f0fdf4;
        --c-text:    #1e293b;
        --c-text2:   #64748b;
        --c-text3:   #94a3b8;
        --c-border:  #e2e8f0;
        --c-track:   #e2e8f0;
        --c-input:   #ffffff;
        --c-expander:#ffffff;
        --c-metric:  #ffffff;
    }

    /* ── Variables de color (modo oscuro vía JS) ── */
    [data-theme="dark"] {
        --c-card:    #1e293b;
        --c-done:    rgba(16,185,129,0.07);
        --c-text:    #f1f5f9;
        --c-text2:   #94a3b8;
        --c-text3:   #64748b;
        --c-border:  #334155;
        --c-track:   #334155;
        --c-input:   #1e293b;
        --c-expander:#1e293b;
        --c-metric:  #1e293b;
    }

    /* ── Variables (fallback via media query para OS dark) ── */
    @media (prefers-color-scheme: dark) {
        :root:not([data-theme="light"]) {
            --c-card:    #1e293b;
            --c-done:    rgba(16,185,129,0.07);
            --c-text:    #f1f5f9;
            --c-text2:   #94a3b8;
            --c-text3:   #64748b;
            --c-border:  #334155;
            --c-track:   #334155;
            --c-input:   #1e293b;
            --c-expander:#1e293b;
            --c-metric:  #1e293b;
        }
    }

    /* ── Background de la app ── */
    [data-theme="light"] .stApp,
    :root:not([data-theme="dark"]) .stApp {
        background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%);
    }
    [data-theme="dark"] .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1a1340 100%) !important;
    }

    /* ── Main block ── */
    .main .block-container {
        padding: 2rem 2.5rem 3rem 2.5rem;
        max-width: 960px;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4f46e5 0%, #7c3aed 100%);
        border-right: none;
    }
    section[data-testid="stSidebar"] * { color: rgba(255,255,255,0.9) !important; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMarkdown p {
        color: rgba(255,255,255,0.75) !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] [data-baseweb="select"] {
        background: rgba(255,255,255,0.15) !important;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    section[data-testid="stSidebar"] [data-baseweb="select"] * {
        background: transparent !important;
    }

    /* ── Botones principales ── */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1.4rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(99,102,241,0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99,102,241,0.45);
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
    }
    .stButton > button:active { transform: translateY(0px); }

    /* ── Form submit ── */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        width: 100%;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(99,102,241,0.3) !important;
    }
    .stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99,102,241,0.45) !important;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        border-radius: 10px !important;
        border: 2px solid var(--c-border) !important;
        background: var(--c-input) !important;
        color: var(--c-text) !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.95rem !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    }

    /* ── Selectbox ── */
    [data-baseweb="select"] > div {
        border-radius: 10px !important;
        border: 2px solid var(--c-border) !important;
        background: var(--c-input) !important;
    }

    /* ── Progress bar ── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
        border-radius: 99px;
    }
    .stProgress > div > div {
        border-radius: 99px;
        background: var(--c-track);
        height: 10px !important;
    }

    /* ── Metrics ── */
    [data-testid="metric-container"] {
        background: var(--c-metric);
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid var(--c-border);
    }
    [data-testid="metric-container"] label {
        color: var(--c-text2) !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: var(--c-text) !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    /* ── Alerts ── */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 10px !important;
        border: none !important;
    }

    /* ── Expander ── */
    .stExpander {
        background: var(--c-expander) !important;
        border-radius: 14px !important;
        border: 1px solid var(--c-border) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        overflow: hidden;
    }
    .stExpander > details > summary {
        font-weight: 600 !important;
        color: var(--c-text) !important;
        padding: 1rem 1.2rem !important;
    }

    /* ── Divider ── */
    hr { border-color: var(--c-border) !important; margin: 1.2rem 0 !important; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(99,102,241,0.07);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        color: var(--c-text2);
    }
    .stTabs [aria-selected="true"] {
        background: var(--c-card) !important;
        color: #6366f1 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    /* ── Checkbox ── */
    .stCheckbox label span { font-weight: 500; color: var(--c-text); }

    /* ── Labels generales ── */
    label, .stMarkdown p { color: var(--c-text2); }
    </style>
    """, unsafe_allow_html=True)

def init_session_state():
    defaults = {
        "authenticated": False,
        "token": None,
        "user_email": None,
        "active_timer": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def main():
    inject_css()
    inject_theme_detector()
    init_session_state()

    if not st.session_state.authenticated:
        login_register_screen()
    else:
        with st.sidebar:
            st.markdown("## ⚡ TaskFlow")
            st.markdown("---")
            page = st.selectbox("Navegación", ["Mis Tareas", "Perfil"])
            st.markdown("---")
            st.markdown(f"👤 **{st.session_state.user_email}**")
            if st.button("Cerrar sesión", key="sidebar_logout"):
                for key in ["authenticated", "token", "user_email", "active_timer"]:
                    st.session_state[key] = None if key != "authenticated" else False
                st.rerun()

        if page == "Mis Tareas":
            todo_list_screen()
        elif page == "Perfil":
            profile_screen()

if __name__ == "__main__":
    main()
