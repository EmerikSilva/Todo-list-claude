import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from api_client import (
    get_todos, create_todo, update_todo,
    delete_todo, add_time_log, get_user_profile,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt_seconds(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}h {m:02d}m"
    if m > 0:
        return f"{m}m {s:02d}s"
    return f"{s}s"


# ── Modal de edición ──────────────────────────────────────────────────────────

@st.dialog("Editar tarea", width="large")
def edit_todo_dialog(todo: dict):
    is_done = todo["completed"]
    has_time = todo.get("total_seconds", 0) > 0

    # Cabecera informativa del modal
    badge_color = "#10b981" if is_done else "#6366f1"
    badge_text  = "Completada" if is_done else "Pendiente"
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:1.4rem;">
        <span style="font-size:1.3rem;">{"✅" if is_done else "📋"}</span>
        <div>
            <h3 style="margin:0; color:var(--c-text); font-weight:700;
                       font-size:1.15rem; line-height:1.3;">
                {todo['title']}
            </h3>
            <span style="font-size:0.78rem; font-weight:600; color:{badge_color};
                         background:{badge_color}18; padding:2px 8px;
                         border-radius:99px;">
                {badge_text}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if has_time:
        est   = todo.get("estimated_hours") or 0
        total = todo["total_seconds"]
        info  = f"⏱ **{fmt_seconds(total)}** registradas"
        if est > 0:
            pct   = min(total / (est * 3600) * 100, 100)
            info += f" de **{est}h** estimadas · {pct:.0f}%"
        st.info(info)

    st.markdown("---")

    # Campos editables
    new_title = st.text_input("Título", value=todo["title"])
    new_desc  = st.text_area(
        "Descripción", value=todo.get("description") or "",
        height=100, placeholder="Describe la tarea (opcional)…",
    )
    new_est = st.number_input(
        "Estimación de tiempo (horas)",
        min_value=0.0, step=0.5, format="%.1f",
        value=float(todo.get("estimated_hours") or 0),
        help="0 = sin estimación",
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Guardar cambios", type="primary", use_container_width=True):
            if new_title.strip():
                update_todo(
                    todo["id"], new_title.strip(), new_desc.strip(),
                    is_done, new_est if new_est > 0 else None,
                )
                st.session_state.editing_todo_id = None
                st.rerun()
            else:
                st.error("El título no puede estar vacío.")
    with c2:
        if st.button("✕ Cancelar", use_container_width=True, type="secondary"):
            st.session_state.editing_todo_id = None
            st.rerun()


# ── Barra de progreso tiempo ──────────────────────────────────────────────────

def time_progress_bar(todo: dict):
    est       = todo.get("estimated_hours") or 0
    total_sec = todo.get("total_seconds") or 0
    if est <= 0:
        return

    ratio = min(total_sec / (est * 3600), 1.0)
    pct   = ratio * 100

    if ratio < 0.6:
        color, label = "#10b981", "En tiempo"
    elif ratio < 0.9:
        color, label = "#f59e0b", "Cerca del límite"
    elif ratio < 1.0:
        color, label = "#ef4444", "Por agotar"
    else:
        color, label = "#dc2626", "Tiempo superado"

    est_str = f"{int(est)}h" if est == int(est) else f"{est:.1f}h"

    st.markdown(f"""
    <div style="margin:10px 0 4px;">
        <div style="display:flex; justify-content:space-between;
                    align-items:center; margin-bottom:6px;">
            <span style="font-size:0.8rem; color:var(--c-text2); font-weight:500;">
                ⏱ {fmt_seconds(total_sec)} de {est_str} estimadas
            </span>
            <span style="font-size:0.75rem; font-weight:700; color:{color};
                         background:{color}22; padding:2px 8px; border-radius:99px;">
                {label} · {pct:.0f}%
            </span>
        </div>
        <div style="background:var(--c-track); border-radius:99px;
                    height:7px; overflow:hidden;">
            <div style="background:{color}; width:{pct:.1f}%; height:100%;
                        border-radius:99px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Cronómetro en tiempo real ─────────────────────────────────────────────────

def live_timer(start_time: datetime):
    elapsed = int((datetime.now() - start_time).total_seconds())
    components.html(f"""
    <div style="font-family:'Inter',sans-serif; display:inline-flex;
                align-items:center; gap:8px;
                background:rgba(99,102,241,0.1);
                border:1.5px solid rgba(99,102,241,0.25);
                border-radius:10px; padding:7px 14px;">
        <span style="font-size:1.1rem;">⏱</span>
        <span id="t" style="font-size:1.3rem; font-weight:700;
                             color:#6366f1; letter-spacing:0.05em;">
            --:--
        </span>
    </div>
    <script>
    var s={elapsed};
    function pad(n){{return n<10?'0'+n:''+n;}}
    function tick(){{
        s++;
        var h=Math.floor(s/3600),m=Math.floor((s%3600)/60),sec=s%60;
        document.getElementById('t').textContent=
            (h>0?pad(h)+':':'')+pad(m)+':'+pad(sec);
    }}
    tick(); setInterval(tick,1000);
    </script>
    """, height=50)


# ── Tarjeta de tarea ──────────────────────────────────────────────────────────

def todo_card(todo: dict):
    tid      = todo["id"]
    is_done  = todo["completed"]
    active   = st.session_state.get("active_timer")
    is_timing = active is not None and active["todo_id"] == tid

    # Estado visual
    icon = "✅" if is_done else ("🔵" if is_timing else "📋")
    title_weight = "400" if is_done else "600"
    title_color  = "var(--c-text3)" if is_done else "var(--c-text)"
    title_deco   = "line-through" if is_done else "none"

    with st.container(border=True):
        # ── Cabecera de la tarea ──
        if is_timing:
            st.markdown(
                '<span style="font-size:0.75rem; font-weight:700; color:#6366f1;'
                ' background:rgba(99,102,241,0.1); padding:2px 8px;'
                ' border-radius:99px; margin-bottom:6px; display:inline-block;">'
                '⏱ En progreso</span>',
                unsafe_allow_html=True,
            )

        st.markdown(f"""
        <div style="display:flex; align-items:flex-start; gap:10px;
                    margin-bottom:{'4px' if todo.get('description') else '0'};">
            <span style="font-size:1.15rem; margin-top:1px;">{icon}</span>
            <p style="margin:0; font-size:1.05rem; font-weight:{title_weight};
                      color:{title_color}; text-decoration:{title_deco}; line-height:1.4;">
                {todo['title']}
            </p>
        </div>
        {f'<p style="margin:0 0 0 26px; font-size:0.875rem; color:var(--c-text2);">'
          f'{todo["description"]}</p>' if todo.get("description") else ""}
        """, unsafe_allow_html=True)

        # ── Barra de progreso ──
        if todo.get("estimated_hours"):
            time_progress_bar(todo)

        # ── Cronómetro activo / tiempo acumulado ──
        if is_timing:
            live_timer(active["start_time"])
        elif todo.get("total_seconds", 0) > 0 and not todo.get("estimated_hours"):
            st.markdown(
                f'<p style="margin:6px 0 0; font-size:0.82rem; color:var(--c-text2);">'
                f'⏳ <b style="color:var(--c-text);">{fmt_seconds(todo["total_seconds"])}</b>'
                f' registradas</p>',
                unsafe_allow_html=True,
            )

        # ── Separador ──
        st.markdown(
            '<hr style="margin:10px 0 6px; border-color:var(--c-border);">',
            unsafe_allow_html=True,
        )

        # ── Botones de acción ──
        if is_timing:
            c1, c2, c3 = st.columns([4, 4, 2])
            with c1:
                if st.button("⏹ Detener", key=f"stop_{tid}",
                             type="primary", use_container_width=True):
                    dur = (datetime.now() - active["start_time"]).total_seconds()
                    add_time_log(tid, dur)
                    st.session_state.active_timer = None
                    st.rerun()
            with c2:
                if st.button("✔ Completar", key=f"tog_{tid}",
                             type="secondary", use_container_width=True):
                    update_todo(tid, todo["title"], todo.get("description"),
                                True, todo.get("estimated_hours"))
                    st.session_state.active_timer = None
                    st.rerun()
            with c3:
                if st.button("✏️", key=f"edit_{tid}", type="secondary",
                             use_container_width=True, help="Editar tarea"):
                    st.session_state.editing_todo_id  = tid
                    st.session_state._dialog_open = True
                    st.rerun()

        elif is_done:
            c1, c2, c3 = st.columns([5, 2, 2])
            with c1:
                if st.button("↩ Marcar como pendiente", key=f"tog_{tid}",
                             type="secondary", use_container_width=True):
                    update_todo(tid, todo["title"], todo.get("description"),
                                False, todo.get("estimated_hours"))
                    st.rerun()
            with c2:
                if st.button("✏️", key=f"edit_{tid}", type="secondary",
                             use_container_width=True, help="Editar tarea"):
                    st.session_state.editing_todo_id  = tid
                    st.session_state._dialog_open = True
                    st.rerun()
            with c3:
                if st.button("🗑", key=f"del_{tid}", type="secondary",
                             use_container_width=True, help="Eliminar tarea"):
                    delete_todo(tid)
                    st.rerun()

        else:
            c1, c2, c3, c4 = st.columns([4, 4, 2, 2])
            with c1:
                if st.button("▶ Iniciar", key=f"start_{tid}",
                             type="primary", use_container_width=True):
                    st.session_state.active_timer = {
                        "todo_id": tid, "start_time": datetime.now()
                    }
                    st.rerun()
            with c2:
                if st.button("✔ Completar", key=f"tog_{tid}",
                             type="secondary", use_container_width=True):
                    update_todo(tid, todo["title"], todo.get("description"),
                                True, todo.get("estimated_hours"))
                    st.rerun()
            with c3:
                if st.button("✏️", key=f"edit_{tid}", type="secondary",
                             use_container_width=True, help="Editar tarea"):
                    st.session_state.editing_todo_id  = tid
                    st.session_state._dialog_open = True
                    st.rerun()
            with c4:
                if st.button("🗑", key=f"del_{tid}", type="secondary",
                             use_container_width=True, help="Eliminar tarea"):
                    delete_todo(tid)
                    if active and active["todo_id"] == tid:
                        st.session_state.active_timer = None
                    st.rerun()


# ── Pantalla principal ────────────────────────────────────────────────────────

def todo_list_screen():
    profile_data = get_user_profile()
    name = profile_data["name"] if profile_data else st.session_state.user_email

    todos = get_todos()

    # Abrir el modal de edición si fue solicitado.
    # Consumimos el flag _dialog_open ANTES de llamar al dialog para que,
    # si el usuario cierra con ESC, no se vuelva a abrir en el siguiente rerun.
    if st.session_state.get("_dialog_open") and st.session_state.get("editing_todo_id"):
        st.session_state._dialog_open = False
        eid = st.session_state.editing_todo_id
        todo_to_edit = next((t for t in todos if t["id"] == eid), None)
        if todo_to_edit:
            edit_todo_dialog(todo_to_edit)

    # ── Cabecera ──
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
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

    # ── Métricas ──
    total = len(todos)
    done  = sum(1 for t in todos if t["completed"])

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total", total)
    with c2: st.metric("Completadas", done)
    with c3: st.metric("Pendientes", total - done)

    if total > 0:
        st.progress(done / total)

    st.markdown("---")

    # ── Formulario nueva tarea ──
    with st.expander("➕ Nueva tarea", expanded=not todos):
        with st.form("new_todo"):
            col1, col2 = st.columns([3, 1])
            with col1:
                title = st.text_input("Título de la tarea *")
                desc  = st.text_area("Descripción (opcional)", height=80)
            with col2:
                est = st.number_input("Estimación (h)", min_value=0.0,
                                      step=0.5, format="%.1f")
            if st.form_submit_button("Crear tarea"):
                if title.strip():
                    create_todo(title.strip(), desc.strip(), est if est > 0 else None)
                    st.rerun()
                else:
                    st.error("El título es obligatorio.")

    st.markdown("---")

    # ── Lista de tareas ──
    if not todos:
        st.markdown("""
        <div style="text-align:center; padding:3rem 1rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">🎯</div>
            <h3 style="color:var(--c-text2); font-weight:600;">Sin tareas aún</h3>
            <p style="color:var(--c-text3);">Crea tu primera tarea arriba para empezar.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    pending   = [t for t in todos if not t["completed"]]
    completed = [t for t in todos if t["completed"]]

    if pending:
        st.markdown(
            '<h3 style="color:var(--c-text); font-weight:700; margin-bottom:0.5rem;">'
            '📋 Pendientes</h3>',
            unsafe_allow_html=True,
        )
        for todo in pending:
            todo_card(todo)

    if completed:
        st.markdown(
            '<h3 style="color:var(--c-text2); font-weight:700; '
            'margin:1.5rem 0 0.5rem;">✅ Completadas</h3>',
            unsafe_allow_html=True,
        )
        for todo in completed:
            todo_card(todo)
