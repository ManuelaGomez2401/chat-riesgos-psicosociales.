from datetime import date
import pandas as pd
import streamlit as st

from src.auth import (
    init_auth_state,
    is_logged_in,
    sign_in,
    sign_up,
    sign_out,
    current_profile,
    current_role,
    update_my_display_name,
    list_profiles_admin,
    update_profile_role_admin,
)
from src.kpi import (
    default_range,
    my_kpis,
    admin_kpis,
    my_sessions,
    dataframe_from_counts,
)

st.set_page_config(page_title="Conversemos | Usuarios y KPI", page_icon="📊", layout="wide")

st.markdown(
    """
<style>
:root {--green:#527A61;--dark:#294B3E;--sage:#EAF3EC;--border:#DCE8E0;--warm:#FFFDF9;--muted:#73867C;}
.stApp {background:#F7FAF8;}
.block-container {max-width:1180px;padding-top:1.2rem;}
.kpi-card {background:var(--warm);border:1px solid var(--border);border-radius:18px;padding:18px;min-height:110px;}
.kpi-label {color:var(--muted);font-size:.88rem;}
.kpi-value {color:var(--dark);font-size:2rem;font-weight:750;margin-top:8px;}
.hero {background:linear-gradient(135deg,#527A61,#8EAF98);color:white;border-radius:22px;padding:22px;margin-bottom:16px;}
.hero h1 {margin:0;color:white;}
.hero p {margin:.4rem 0 0;}
</style>
""",
    unsafe_allow_html=True,
)

init_auth_state()


def kpi_card(label, value):
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>',
        unsafe_allow_html=True,
    )


def login_screen():
    st.markdown('<div class="hero"><h1>Conversemos</h1><p>Acceso de usuarios e indicadores del prototipo académico.</p></div>', unsafe_allow_html=True)
    login_tab, signup_tab = st.tabs(["Iniciar sesión", "Crear cuenta"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Correo")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar", type="primary", use_container_width=True)
        if submit:
            try:
                sign_in(email.strip(), password)
                st.rerun()
            except Exception as exc:
                st.error(f"No fue posible iniciar sesión: {exc}")

    with signup_tab:
        with st.form("signup_form"):
            display_name = st.text_input("Nombre visible o alias")
            email = st.text_input("Correo", key="signup_email")
            password = st.text_input("Contraseña", type="password", key="signup_password")
            confirm = st.text_input("Confirmar contraseña", type="password")
            submit = st.form_submit_button("Crear cuenta", use_container_width=True)
        if submit:
            if len(password) < 8:
                st.error("La contraseña debe tener al menos 8 caracteres.")
            elif password != confirm:
                st.error("Las contraseñas no coinciden.")
            elif not display_name.strip():
                st.error("Escribe un nombre visible o alias.")
            else:
                try:
                    response = sign_up(email.strip(), password, display_name.strip())
                    st.success(response["message"])
                    if response["confirmed"]:
                        st.rerun()
                except Exception as exc:
                    st.error(f"No fue posible crear la cuenta: {exc}")


if not is_logged_in():
    login_screen()
    st.stop()

profile = current_profile()
role = current_role()

with st.sidebar:
    st.subheader(profile.get("display_name") or st.session_state.auth_email)
    st.caption(f"Rol: {role}")
    options = ["Mi resumen", "Mi historial", "Mi perfil"]
    if role in {"reviewer", "admin"}:
        options.append("KPI globales")
    if role == "admin":
        options.append("Usuarios")
    page = st.radio("Menú", options)
    if st.button("Cerrar sesión", use_container_width=True):
        sign_out()
        st.rerun()

st.markdown('<div class="hero"><h1>Panel de Conversemos</h1><p>Indicadores personales y académicos según el rol autorizado.</p></div>', unsafe_allow_html=True)

start_default, end_default = default_range(30)

if page == "Mi resumen":
    st.subheader("Mi resumen de bienestar")
    d1, d2 = st.columns(2)
    start = d1.date_input("Desde", start_default, max_value=date.today())
    end = d2.date_input("Hasta", end_default, max_value=date.today())
    if start > end:
        st.error("La fecha inicial no puede ser posterior a la final.")
        st.stop()
    data = my_kpis(start, end)
    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("Conversaciones", data.get("total_sessions", 0))
    with c2: kpi_card("Finalizadas", data.get("completed_sessions", 0))
    with c3: kpi_card("Tasa de finalización", f'{data.get("completion_rate", 0):.1f}%')

    left, right = st.columns(2)
    with left:
        st.markdown("### Dimensiones conversadas")
        df = dataframe_from_counts(data.get("dimensions"), "Dimensión", "Conversaciones")
        if df.empty: st.info("Todavía no existen dimensiones en el periodo.")
        else: st.bar_chart(df.set_index("Dimensión"))
    with right:
        st.markdown("### Orientaciones")
        df = dataframe_from_counts(data.get("orientations"), "Orientación", "Conversaciones")
        if df.empty: st.info("Todavía no existen orientaciones en el periodo.")
        else: st.bar_chart(df.set_index("Orientación"))

elif page == "Mi historial":
    st.subheader("Mi historial")
    rows = my_sessions()
    if not rows:
        st.info("Aún no tienes conversaciones almacenadas con esta cuenta.")
    for row in rows:
        result = (row.get("results") or [{}])[0] if isinstance(row.get("results"), list) else (row.get("results") or {})
        with st.expander(f'{row.get("started_at", "Sin fecha")} · {row.get("status", "sin estado")}'):
            st.write("**Dimensiones:**", ", ".join(result.get("dimensions") or []) or "Sin dimensión")
            st.write("**Frecuencia:**", result.get("frequency") or "Sin registro")
            st.write("**Duración:**", result.get("duration") or "Sin registro")
            st.write("**Orientación:**", result.get("orientation") or "Sin resultado")
            st.caption("El resumen no constituye un diagnóstico.")

elif page == "Mi perfil":
    st.subheader("Mi perfil")
    with st.form("profile_form"):
        display_name = st.text_input("Nombre visible", value=profile.get("display_name") or "")
        st.text_input("Correo", value=st.session_state.auth_email or "", disabled=True)
        st.text_input("Rol", value=role, disabled=True)
        submit = st.form_submit_button("Guardar cambios")
    if submit:
        try:
            update_my_display_name(display_name.strip())
            st.success("Perfil actualizado.")
            st.rerun()
        except Exception as exc:
            st.error(f"No fue posible actualizar el perfil: {exc}")

elif page == "KPI globales":
    st.subheader("KPI académicos globales")
    st.info("Estos indicadores son agregados. No muestran conversaciones individuales.")
    d1, d2 = st.columns(2)
    start = d1.date_input("Desde", start_default, key="admin_start", max_value=date.today())
    end = d2.date_input("Hasta", end_default, key="admin_end", max_value=date.today())
    data = admin_kpis(start, end)
    cols = st.columns(4)
    labels = [
        ("Usuarios activos", data.get("active_users", 0)),
        ("Conversaciones", data.get("total_sessions", 0)),
        ("Finalización", f'{data.get("completion_rate", 0):.1f}%'),
        ("Gemini exitoso", f'{data.get("gemini_success_rate", 0):.1f}%'),
    ]
    for col, (label, value) in zip(cols, labels):
        with col: kpi_card(label, value)
    cols = st.columns(4)
    labels = [
        ("Propuestas pendientes", data.get("pending_proposals", 0)),
        ("Propuestas aprobadas", data.get("approved_proposals", 0)),
        ("Propuestas rechazadas", data.get("rejected_proposals", 0)),
        ("Sin dimensión", data.get("sessions_without_dimension", 0)),
    ]
    for col, (label, value) in zip(cols, labels):
        with col: kpi_card(label, value)

    left, right = st.columns(2)
    with left:
        st.markdown("### Dimensiones")
        df = dataframe_from_counts(data.get("dimensions"), "Dimensión", "Cantidad")
        if not df.empty: st.bar_chart(df.set_index("Dimensión"))
    with right:
        st.markdown("### Orientaciones")
        df = dataframe_from_counts(data.get("orientations"), "Orientación", "Cantidad")
        if not df.empty: st.bar_chart(df.set_index("Orientación"))

elif page == "Usuarios":
    st.subheader("Gestión de usuarios")
    users = list_profiles_admin()
    if not users:
        st.info("No hay usuarios registrados.")
    for user in users:
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.write(f'**{user.get("display_name") or "Sin nombre"}**')
            c1.caption(user.get("id"))
            role_value = c2.selectbox(
                "Rol",
                ["participant", "reviewer", "admin"],
                index=["participant", "reviewer", "admin"].index(user.get("role", "participant")),
                key=f'role_{user["id"]}',
            )
            active = c3.checkbox("Activo", value=bool(user.get("active", True)), key=f'active_{user["id"]}')
            if st.button("Guardar usuario", key=f'save_{user["id"]}'):
                try:
                    update_profile_role_admin(user["id"], role_value, active)
                    st.success("Usuario actualizado.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"No fue posible actualizar el usuario: {exc}")
