import streamlit as st
from api_client import get_user_profile, get_todos
from todo_screen import fmt_seconds

def profile_screen():
    profile_data = get_user_profile()
    todos = get_todos()

    name = profile_data["name"] if profile_data else st.session_state.user_email

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);
                border-radius:20px; padding:2rem 2.5rem; margin-bottom:2rem;
                box-shadow:0 8px 32px rgba(99,102,241,0.3);">
        <div style="display:flex; align-items:center; gap:1.2rem;">
            <div style="background:rgba(255,255,255,0.2); border-radius:50%;
                        width:64px; height:64px; display:flex; align-items:center;
                        justify-content:center; font-size:1.8rem;">
                👤
            </div>
            <div>
                <h2 style="margin:0; color:white; font-weight:800; font-size:1.6rem;">
                    {name}
                </h2>
                <p style="margin:4px 0 0 0; color:rgba(255,255,255,0.75); font-size:0.9rem;">
                    {profile_data["email"] if profile_data else st.session_state.user_email}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not profile_data:
        st.warning("No se pudo cargar la información del perfil.")

    if todos:
        total = len(todos)
        done = sum(1 for t in todos if t["completed"])
        pending = total - done
        total_seconds = sum(t.get("total_seconds", 0) for t in todos)
        total_estimated = sum((t.get("estimated_hours") or 0) * 3600 for t in todos)

        st.markdown("### 📊 Estadísticas")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total", total)
        with c2:
            st.metric("✅ Completadas", done)
        with c3:
            st.metric("⏳ Pendientes", pending)
        with c4:
            st.metric("⏱ Tiempo registrado", fmt_seconds(total_seconds))

        if total > 0:
            rate = done / total
            st.markdown(f"""
            <div style="margin:1rem 0 0.4rem;">
                <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                    <span style="font-size:0.9rem; color:#64748b; font-weight:500;">Tasa de completado</span>
                    <span style="font-weight:700; color:#6366f1;">{rate*100:.0f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(rate)

        if total_estimated > 0:
            st.markdown("---")
            st.markdown("### ⏱ Tiempo estimado vs. registrado")
            ratio = min(total_seconds / total_estimated, 1.0)
            est_str = fmt_seconds(total_estimated)
            reg_str = fmt_seconds(total_seconds)
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="font-size:0.9rem; color:#64748b;">Registrado: <b>{reg_str}</b></span>
                <span style="font-size:0.9rem; color:#64748b;">Estimado: <b>{est_str}</b></span>
            </div>
            """, unsafe_allow_html=True)
            st.progress(ratio)

        st.markdown("---")
        st.markdown("### 📋 Detalle de tareas")
        for todo in sorted(todos, key=lambda t: t["completed"]):
            est = todo.get("estimated_hours") or 0
            logged = todo.get("total_seconds") or 0
            ratio_t = min(logged / (est * 3600), 1.0) if est > 0 else 0
            color = "#10b981" if todo["completed"] else "#6366f1"

            st.markdown(f"""
            <div style="background:white; border-radius:12px; padding:14px 18px;
                        border-left:4px solid {color}; margin-bottom:10px;
                        box-shadow:0 1px 6px rgba(0,0,0,0.05);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:600; color:#1e293b;">
                        {"✅" if todo["completed"] else "📋"} {todo["title"]}
                    </span>
                    <span style="font-size:0.82rem; color:#64748b;">
                        {fmt_seconds(logged)} registradas
                        {f"/ {est}h estimadas" if est > 0 else ""}
                    </span>
                </div>
                {f'''<div style="background:#e2e8f0;border-radius:99px;height:6px;margin-top:8px;overflow:hidden;">
                    <div style="background:{color};width:{ratio_t*100:.1f}%;height:100%;border-radius:99px;"></div>
                </div>''' if est > 0 else ""}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:3rem 1rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">🎯</div>
            <p style="color:#94a3b8;">Aún no tienes tareas. ¡Crea una para empezar!</p>
        </div>
        """, unsafe_allow_html=True)
