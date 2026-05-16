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

# JS inyectado en un iframe de altura 0.
# Lee el color de fondo real del .stApp de Streamlit y pone
# data-theme="light" | "dark" en el <html> del documento padre.
# Esto es lo ÚNICO que controla el tema — sin @media (prefers-color-scheme).
_THEME_DETECTOR_JS = """
<script>
(function () {
    var INTERVAL = 900;   // ms entre comprobaciones
    var lastTheme = null;

    function detect() {
        try {
            var doc  = window.parent.document;
            // Preferimos stAppViewContainer porque es el contenedor raíz real
            var app  = doc.querySelector('[data-testid="stAppViewContainer"]')
                    || doc.querySelector('.stApp');
            if (!app) { setTimeout(detect, INTERVAL); return; }

            var bg = window.parent.getComputedStyle(app).backgroundColor;
            var m  = bg.match(/\d+/g);
            if (!m || m.length < 3) { setTimeout(detect, INTERVAL); return; }

            var brightness = (parseInt(m[0]) * 299
                            + parseInt(m[1]) * 587
                            + parseInt(m[2]) * 114) / 1000;

            // Streamlit dark bg (rgb 14,17,23) → brightness ≈ 16
            // Streamlit light bg (rgb 255,255,255) → brightness = 255
            var theme = brightness < 100 ? 'dark' : 'light';

            if (theme !== lastTheme) {
                doc.documentElement.setAttribute('data-theme', theme);
                lastTheme = theme;
            }
        } catch (e) { /* cross-origin guard */ }
        setTimeout(detect, INTERVAL);
    }

    // Primer disparo inmediato, luego bucle
    detect();
})();
</script>
"""

def inject_theme_detector():
    components.html(_THEME_DETECTOR_JS, height=0, scrolling=False)

def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ═══════════════════════════════════════════════════════
   VARIABLES — modo CLARO (valores por defecto en :root)
   ══════════════════════════════════════════════════════ */
:root {
    --c-card:     #ffffff;
    --c-done:     #f0fdf4;
    --c-text:     #0f172a;   /* casi negro   — máximo contraste */
    --c-text2:    #374151;   /* gris oscuro  — claramente legible */
    --c-text3:    #4b5563;   /* gris medio   — legible */
    --c-border:   #cbd5e1;
    --c-track:    #e2e8f0;
    --c-input:    #ffffff;
    --c-metric:   #ffffff;
    --c-expander: #ffffff;
    --c-app-bg:   linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%);
}

/* ═══════════════════════════════════════════════════════
   VARIABLES — modo OSCURO
   Solo se activan cuando el JS pone data-theme="dark".
   NO usamos @media (prefers-color-scheme) para evitar que
   el OS dark mode choque con el tema claro de Streamlit.
   ══════════════════════════════════════════════════════ */
[data-theme="dark"] {
    --c-card:     #1e293b;
    --c-done:     rgba(16,185,129,0.08);
    --c-text:     #f1f5f9;   /* casi blanco  — máximo contraste */
    --c-text2:    #cbd5e1;   /* gris claro   — claramente legible */
    --c-text3:    #94a3b8;   /* gris medio   — legible */
    --c-border:   #334155;
    --c-track:    #334155;
    --c-input:    #263348;
    --c-metric:   #1e293b;
    --c-expander: #1e293b;
    --c-app-bg:   linear-gradient(135deg, #0f172a 0%, #1a1340 100%);
}

/* ═══════════════════════════════════════════════════════
   APP BACKGROUND
   ══════════════════════════════════════════════════════ */
.stApp { background: var(--c-app-bg) !important; }

/* ── Main block ── */
.main .block-container {
    padding: 2rem 2.5rem 3rem 2.5rem;
    max-width: 960px;
}

/* ═══════════════════════════════════════════════════════
   SIDEBAR — gradiente fijo (siempre legible en ambos modos)
   ══════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #4f46e5 0%, #7c3aed 100%);
    border-right: none;
}
section[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.92) !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMarkdown p {
    color: rgba(255,255,255,0.72) !important;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
}
section[data-testid="stSidebar"] [data-baseweb="select"] {
    background: rgba(255,255,255,0.15) !important;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.25) !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] * {
    background: transparent !important;
}

/* ═══════════════════════════════════════════════════════
   BOTONES — primarios (gradiente)
   ══════════════════════════════════════════════════════ */
.stButton > button[kind="primary"],
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.3) !important;
}
[data-testid="baseButton-primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.45) !important;
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
}
[data-testid="baseButton-primary"]:active { transform: translateY(0) !important; }

/* Fallback: cualquier botón sin kind explícito */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #ffffff !important;
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
.stButton > button:active { transform: translateY(0); }

/* Botones secundarios — estilo ghost */
[data-testid="baseButton-secondary"] {
    background: transparent !important;
    color: var(--c-text2) !important;
    border: 1.5px solid var(--c-border) !important;
    box-shadow: none !important;
}
[data-testid="baseButton-secondary"]:hover {
    background: rgba(99,102,241,0.08) !important;
    border-color: #6366f1 !important;
    color: #6366f1 !important;
    transform: translateY(-1px) !important;
    box-shadow: none !important;
}

.stFormSubmitButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #ffffff !important;
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

/* ═══════════════════════════════════════════════════════
   INPUTS (usan variables para adaptarse al tema)
   ══════════════════════════════════════════════════════ */
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
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    outline: none !important;
}
/* Labels de inputs */
.stTextInput label, .stTextArea label,
.stNumberInput label, .stSelectbox label {
    color: var(--c-text2) !important;
    font-weight: 500 !important;
}

/* ═══════════════════════════════════════════════════════
   SELECTBOX
   ══════════════════════════════════════════════════════ */
[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border: 2px solid var(--c-border) !important;
    background: var(--c-input) !important;
    color: var(--c-text) !important;
}

/* ═══════════════════════════════════════════════════════
   PROGRESS BAR
   ══════════════════════════════════════════════════════ */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
    border-radius: 99px;
}
.stProgress > div > div {
    border-radius: 99px;
    background: var(--c-track);
    height: 10px !important;
}

/* ═══════════════════════════════════════════════════════
   METRICS
   ══════════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: var(--c-metric) !important;
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
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

/* ═══════════════════════════════════════════════════════
   ALERTS
   ══════════════════════════════════════════════════════ */
.stSuccess, .stInfo, .stWarning, .stError,
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: none !important;
}

/* ═══════════════════════════════════════════════════════
   EXPANDER
   ══════════════════════════════════════════════════════ */
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

/* ═══════════════════════════════════════════════════════
   DIVIDER
   ══════════════════════════════════════════════════════ */
hr { border-color: var(--c-border) !important; margin: 1.2rem 0 !important; }

/* ═══════════════════════════════════════════════════════
   TABS
   ══════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(99,102,241,0.08);
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
    color: var(--c-text2);
    background: transparent;
}
.stTabs [aria-selected="true"] {
    background: var(--c-card) !important;
    color: #6366f1 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

/* ═══════════════════════════════════════════════════════
   CHECKBOX / texto general
   ══════════════════════════════════════════════════════ */
.stCheckbox label span,
label,
p { color: var(--c-text2); }

/* ═══════════════════════════════════════════════════════
   TARJETAS (st.container border=True)
   ══════════════════════════════════════════════════════ */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--c-card) !important;
    border-radius: 16px !important;
    border: 1px solid var(--c-border) !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    padding: 1.2rem 1.4rem !important;
    margin-bottom: 0.75rem !important;
    transition: box-shadow 0.2s, transform 0.2s;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 6px 24px rgba(99,102,241,0.12);
    transform: translateY(-1px);
}

/* ═══════════════════════════════════════════════════════
   MODAL DE EDICIÓN (@st.dialog)
   ══════════════════════════════════════════════════════ */
[data-testid="stModal"] > div,
[data-testid="stModal"] > div > div {
    background: var(--c-card) !important;
    border-radius: 20px !important;
    border: 1px solid var(--c-border) !important;
}
/* Overlay backdrop */
[data-testid="stModal"] {
    background: rgba(0,0,0,0.5) !important;
    backdrop-filter: blur(4px);
}
</style>
""", unsafe_allow_html=True)

def init_session_state():
    defaults = {
        "authenticated": False,
        "token": None,
        "user_email": None,
        "active_timer": None,
        "editing_todo_id": None,
        "_dialog_open": False,
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
                for key in ["token", "user_email", "active_timer",
                            "editing_todo_id"]:
                    st.session_state[key] = None
                st.session_state.authenticated = False
                st.session_state._dialog_open = False
                st.rerun()

        if page == "Mis Tareas":
            todo_list_screen()
        elif page == "Perfil":
            profile_screen()

if __name__ == "__main__":
    main()
