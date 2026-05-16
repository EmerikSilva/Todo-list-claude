import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from api_client import get_todos, create_todo, update_todo, delete_todo, add_time_log, get_user_profile

def fmt_seconds(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}h {m:02d}m"
    elif m > 0:
        return f"{m}m {s:02d}s"
    return f"{s}s"

def time_progress_bar(todo):
    est = todo.get("estimated_hours") or 0
    total_sec = todo.get("total_seconds") or 0
    if est <= 0:
        return

    ratio = min(total_sec / (est * 3600), 1.0)
    pct = ratio * 100

    if ratio < 0.6:
        color, label = "#10b981", "En tiempo"
    elif ratio < 0.9:
        color, label = "#f59e0b", "Cerca del límite"
    elif ratio < 1.0:
        color, label = "#ef4444", "Por agotar"
    else:
        color, label = "#dc2626", "Tiempo superado"

    est_str = f"{est}h" if est == int(est) else f"{est:.1f}h"

    st.markdown(f"""
    <div style="margin:8px 0 4px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="font-size:0.82rem; color:var(--c-text2); font-weight:500;">
                ⏱ {fmt_seconds(total_sec)} registradas de {est_str} estimadas
            </span>
            <span style="font-size:0.78rem; font-weight:700; color:{color};
                         background:{color}22; padding:2px 8px; border-radius:99px;">
                {label} · {pct:.0f}%
            </span>
        </div>
        <div style="background:var(--c-track); border-radius:99px; height:8px; overflow:hidden;">
            <div style="background:{color}; width:{pct:.1f}%; height:100%;
                        border-radius:99px; transition:width 0.4s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def live_timer(start_time: datetime):
    elapsed = int((datetime.now() - start_time).total_seconds())
    components.html(f"""
    <div style="font-family:'Inter',sans-serif; display:inline-flex; align-items:center; gap:10px;
                background:rgba(99,102,241,0.12); border:1.5px solid rgba(99,102,241,0.3);
                border-radius:12px; padding:10px 18px;">
        <span style="font-size:1.4rem;">⏱</span>
        <span id="t" style="font-size:1.5rem; font-weight:700; color:#6366f1;
                             letter-spacing:0.04em;">--:--</span>
    </div>
    <script>
        var s = {elapsed};
        function pad(n){{return n<10?'0'+n:''+n;}}
        function tick(){{
            s++;
            var h=Math.floor(s/3600), m=Math.floor((s%3600)/60), sec=s%60;
            document.getElementById('t').textContent =
                (h>0 ? pad(h)+':' : '') + pad(m) + ':' + pad(sec);
        }}
        tick();
        setInterval(tick, 1000);
    </script>
    """, height=60)

def todo_card(todo):
    tid = todo["id"]
    is_done = todo["completed"]
    active = st.session_state.active_timer
    is_timing = active is not None and active["todo_id"] == tid

    if is_timing:
        border_color = "#6366f1"
    elif is_done:
        border_color = "#10b981"
    else:
        border_color = "var(--c-border)"

    bg = "var(--c-done)" if is_done else "var(--c-card)"
    text_color = "var(--c-text3)" if is_done else "var(--c-text)"
    text_deco = "line-through" if is_done else "none"
    icon = "✅" if is_done else ("🔵" if is_timing else "📋")

    st.markdown(f"""
    <div style="background:{bg}; border-radius:16px; border:1.5px solid {border_color};
                box-shadow:0 2px 16px rgba(0,0,0,0.07); padding:20px 24px 8px;
                margin-bottom:4px;">
        <div style="display:flex; align-items:flex-start; gap:12px;">
            <span style="font-size:1.25rem; margin-top:2px;">{icon}</span>
            <div style="flex:1;">
                <p style="margin:0; font-size:1.05rem; font-weight:{'400' if is_done else '600'};
                           color:{text_color}; text-decoration:{text_deco};">
                    {todo['title']}
                </p>
                {f'<p style="margin:4px 0 0; font-size:0.88rem; color:var(--c-text2);">{todo["description"]}</p>' if todo.get("description") else ""}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if todo.get("estimated_hours"):
        time_progress_bar(todo)

    col_timer, col_actions = st.columns([3, 2])

    with col_timer:
        if is_timing:
            live_timer(active["start_time"])
        elif todo.get("total_seconds", 0) > 0:
            st.markdown(
                f'<span style="font-size:0.85rem; color:var(--c-text2);">⏳ Total acumulado: <b style="color:var(--c-text);">{fmt_seconds(todo["total_seconds"])}</b></span>',
                unsafe_allow_html=True,
            )

    with col_actions:
        if is_timing:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("⏹ Detener", key=f"stop_{tid}"):
                    duration = (datetime.now() - active["start_time"]).total_seconds()
                    add_time_log(tid, duration)
                    st.session_state.active_timer = None
                    st.rerun()
            with c2:
                if st.button("✔ Completar", key=f"tog_{tid}"):
                    update_todo(tid, todo["title"], todo.get("description"), True, todo.get("estimated_hours"))
                    st.rerun()
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                if not is_done:
                    if st.button("▶ Iniciar", key=f"start_{tid}"):
                        st.session_state.active_timer = {"todo_id": tid, "start_time": datetime.now()}
                        st.rerun()
            with c2:
                label = "↩ Pendiente" if is_done else "✔ Completar"
                if st.button(label, key=f"tog_{tid}"):
                    update_todo(tid, todo["title"], todo.get("description"), not is_done, todo.get("estimated_hours"))
                    st.rerun()
            with c3:
                if st.button("🗑", key=f"del_{tid}"):
                    delete_todo(tid)
                    if active and active["todo_id"] == tid:
                        st.session_state.active_timer = None
                    st.rerun()

    with st.expander("✏️ Editar tarea", expanded=False):
        with st.form(key=f"edit_{tid}"):
            new_title = st.text_input("Título", value=todo["title"])
            new_desc = st.text_area("Descripción", value=todo.get("description") or "")
            new_est = st.number_input(
                "Estimación (horas)", min_value=0.0, step=0.5, format="%.1f",
                value=float(todo.get("estimated_hours") or 0),
            )
            if st.form_submit_button("Guardar cambios"):
                update_todo(tid, new_title, new_desc, is_done, new_est if new_est > 0 else None)
                st.rerun()

    st.markdown("<div style='margin-bottom:12px'></div>", unsafe_allow_html=True)

def todo_list_screen():
    profile_data = get_user_profile()
    name = profile_data["name"] if profile_data else st.session_state.user_email

    st.markdown(f"""
    <div style="margin-bottom:2rem;">
        <h1 style="margin:0; font-size:2rem; font-weight:800;
                   background:linear-gradient(135deg,#6366f1,#8b5cf6,#ec4899);
                   -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                   background-clip:text;">
            ⚡ TaskFlow
        </h1>
        <p style="margin:4px 0 0; color:var(--c-text2); font-size:1rem;">
            Hola, <b style="color:var(--c-text);">{name}</b>. Aquí están tus tareas.
        </p>
    </div>
    """, unsafe_allow_html=True)

    todos = get_todos()
    total = len(todos)
    done = sum(1 for t in todos if t["completed"])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total", total)
    with c2:
        st.metric("Completadas", done)
    with c3:
        st.metric("Pendientes", total - done)

    if total > 0:
        st.progress(done / total)

    st.markdown("---")

    with st.expander("➕ Nueva tarea", expanded=not todos):
        with st.form("new_todo"):
            col1, col2 = st.columns([3, 1])
            with col1:
                title = st.text_input("Título de la tarea *")
                desc = st.text_area("Descripción (opcional)", height=80)
            with col2:
                est = st.number_input("Estimación (h)", min_value=0.0, step=0.5, format="%.1f")
            if st.form_submit_button("Crear tarea"):
                if title.strip():
                    create_todo(title.strip(), desc.strip(), est if est > 0 else None)
                    st.rerun()
                else:
                    st.error("El título es obligatorio.")

    st.markdown("---")

    if not todos:
        st.markdown("""
        <div style="text-align:center; padding:3rem 1rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">🎯</div>
            <h3 style="color:var(--c-text2); font-weight:600;">Sin tareas aún</h3>
            <p style="color:var(--c-text3);">Crea tu primera tarea arriba para empezar.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    pending = [t for t in todos if not t["completed"]]
    completed = [t for t in todos if t["completed"]]

    if pending:
        st.markdown('<h3 style="color:var(--c-text); font-weight:700; margin-bottom:1rem;">📋 Pendientes</h3>', unsafe_allow_html=True)
        for todo in pending:
            todo_card(todo)

    if completed:
        st.markdown('<h3 style="color:var(--c-text2); font-weight:700; margin:1.5rem 0 1rem;">✅ Completadas</h3>', unsafe_allow_html=True)
        for todo in completed:
            todo_card(todo)
