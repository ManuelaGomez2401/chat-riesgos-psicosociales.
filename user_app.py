import base64
from datetime import date
from pathlib import Path

import streamlit as st

from src.auth import (
    init_auth_state,
    is_logged_in,
    sign_in,
    sign_up,
    sign_out,
    current_profile,
    current_role,
    update_my_profile,
    list_profiles_admin,
    update_profile_role_admin,
)
from src.kpi import (
    default_range,
    my_kpis,
    admin_kpis,
    demographic_kpis,
    my_sessions,
    dataframe_from_counts,
)


# =========================================================
# CONFIGURACION
# =========================================================

ZIA = "assets/zia.png"

st.set_page_config(
    page_title="SENZIA Indicadores",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# ESTILOS SENZIA
# =========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #070D1A;
        --bg-soft: #0C1426;
        --card: #101B31;
        --card-2: #14213A;
        --text: #F2F5FF;
        --muted: #A7B2C9;
        --cyan: #20D5F5;
        --blue: #3C8DFF;
        --purple: #8067FF;
        --border: #21365A;
        --success: #70D6A0;
    }

    html, body, [class*="css"] { font-family: "Inter", sans-serif; }

    .stApp {
        color: var(--text);
        background:
            radial-gradient(circle at 82% 10%, rgba(60,141,255,.14), transparent 25%),
            radial-gradient(circle at 8% 75%, rgba(32,213,245,.08), transparent 30%),
            linear-gradient(180deg, #070D1A, #080F1E);
    }

    .block-container { max-width: 1180px; padding-top: 1.1rem; padding-bottom: 5rem; }
    header[data-testid="stHeader"] { background: transparent; }

    [data-testid="stSidebar"] {
        background: #080F1E;
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] * { color: var(--text); }

    .senzia-hero {
        position: relative;
        overflow: hidden;
        padding: 28px;
        margin-bottom: 18px;
        border: 1px solid var(--border);
        border-radius: 26px;
        background: linear-gradient(135deg, rgba(16,27,49,.98), rgba(11,20,40,.98));
        box-shadow: 0 24px 70px rgba(0,0,0,.25);
    }

    .senzia-hero-content {
        position: relative;
        z-index: 2;
        display: grid;
        grid-template-columns: 1fr 180px;
        align-items: center;
        gap: 24px;
    }

    .eyebrow {
        display: inline-flex;
        width: fit-content;
        padding: 7px 13px;
        border: 1px solid rgba(32,213,245,.22);
        border-radius: 999px;
        color: var(--cyan);
        background: rgba(32,213,245,.07);
        font-size: .79rem;
        font-weight: 650;
    }

    .brand {
        margin: 12px 0 0;
        color: var(--text);
        font-size: 2.25rem;
        font-weight: 800;
        letter-spacing: .06em;
    }

    .module {
        margin-top: 8px;
        background: linear-gradient(90deg, var(--cyan), var(--purple));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        font-size: 1.1rem;
        font-weight: 750;
    }

    .description { color: var(--muted); line-height: 1.62; max-width: 700px; }

    .zia-shell {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 150px;
        border: 1px solid rgba(60,141,255,.3);
        border-radius: 23px;
        background: radial-gradient(circle, rgba(32,213,245,.16), rgba(128,103,255,.05) 58%, transparent 72%);
    }

    .zia-shell img {
        width: 125px;
        height: 125px;
        object-fit: cover;
        border: 2px solid rgba(32,213,245,.55);
        border-radius: 50%;
        box-shadow: 0 0 28px rgba(32,213,245,.22);
    }

    .auth-card, .info-card {
        padding: 18px;
        border: 1px solid var(--border);
        border-radius: 20px;
        background: rgba(16,27,49,.92);
    }

    .kpi-card {
        min-height: 122px;
        padding: 18px;
        border: 1px solid var(--border);
        border-radius: 19px;
        background: linear-gradient(145deg, rgba(16,27,49,.97), rgba(13,23,43,.97));
    }

    .kpi-label { color: var(--muted); font-size: .86rem; }
    .kpi-value { margin-top: 9px; color: var(--cyan); font-size: 2rem; font-weight: 800; }

    .stButton > button {
        min-height: 42px;
        color: var(--text);
        border: 1px solid var(--border);
        border-radius: 14px;
        background: var(--card);
        font-weight: 650;
    }

    .stButton > button[kind="primary"] {
        color: #07101A;
        border: none;
        background: linear-gradient(135deg, var(--cyan), var(--purple));
    }

    [data-testid="stTextInput"] input,
    [data-testid="stDateInput"] input,
    [data-testid="stSelectbox"] > div > div {
        color: var(--text);
        border-color: var(--border);
        background: var(--card);
    }

    [data-testid="stTabs"] button { color: var(--muted); }
    [data-testid="stTabs"] button[aria-selected="true"] { color: var(--cyan); }
    [data-testid="stExpander"] { border: 1px solid var(--border); background: rgba(16,27,49,.85); }

    @media (max-width: 720px) {
        .block-container { padding: .8rem .8rem 4rem; }
        .senzia-hero-content { grid-template-columns: 1fr; }
        .zia-shell { display: none; }
        .brand { font-size: 1.8rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def image_b64(path):
    file_path = Path(path)
    if not file_path.exists():
        return ""
    return base64.b64encode(file_path.read_bytes()).decode()


def hero(title, subtitle, description):
    encoded = image_b64(ZIA)
    visual = (
        f'<img src="data:image/png;base64,{encoded}" alt="Zia">'
        if encoded
        else '<div style="font-size:72px;color:#20D5F5">✦</div>'
    )
    st.markdown(
        f"""
        <section class="senzia-hero">
            <div class="senzia-hero-content">
                <div>
                    <div class="eyebrow">Inteligencia · Bienestar · Transformación</div>
                    <h1 class="brand">{title}</h1>
                    <div class="module">{subtitle}</div>
                    <p class="description">{description}</p>
                </div>
                <div class="zia-shell">{visual}</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label, value):
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>',
        unsafe_allow_html=True,
    )


def age_on_date(birth_date, reference_date=None):
    reference_date = reference_date or date.today()
    return (
        reference_date.year
        - birth_date.year
        - ((reference_date.month, reference_date.day) < (birth_date.month, birth_date.day))
    )


init_auth_state()


# =========================================================
# ACCESO Y REGISTRO
# =========================================================

def login_screen():
    hero(
        "SENZIA",
        "Acceso a indicadores y bienestar organizacional",
        "Consulta tu historial, tus indicadores personales y, según tu rol, métricas académicas agregadas de la plataforma.",
    )

    login_tab, signup_tab = st.tabs(["Iniciar sesión", "Crear cuenta"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Correo")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button(
                "Ingresar",
                type="primary",
                use_container_width=True,
            )
        if submit:
            try:
                sign_in(email.strip(), password)
                st.rerun()
            except Exception as exc:
                st.error(f"No fue posible iniciar sesión: {exc}")

    with signup_tab:
        st.info(
            "La fecha de nacimiento permite calcular el rango de edad correspondiente a cada conversación. "
            "El género se usa únicamente para KPI agregados y no modifica la orientación individual."
        )
        with st.form("signup_form"):
            display_name = st.text_input("Nombre visible o alias")
            email = st.text_input("Correo", key="signup_email")
            password = st.text_input("Contraseña", type="password", key="signup_password")
            confirm = st.text_input("Confirmar contraseña", type="password")

            max_birth_date = date(date.today().year - 18, date.today().month, date.today().day)
            birth_date = st.date_input(
                "Fecha de nacimiento",
                value=date(1995, 1, 1),
                min_value=date(1940, 1, 1),
                max_value=max_birth_date,
                format="DD/MM/YYYY",
                help="SENZIA calcula la edad que tenías cuando ocurrió cada conversación.",
            )

            gender = st.selectbox(
                "Género",
                [
                    "Prefiero no responder",
                    "Mujer",
                    "Hombre",
                    "No binario",
                    "Otra identidad",
                ],
            )

            demographic_consent = st.checkbox(
                "Autorizo el uso de mi fecha de nacimiento y género para análisis académicos agregados."
            )
            st.caption(
                "Estos datos no se utilizan para diagnosticar, clasificar riesgo individual ni tomar decisiones laborales."
            )

            submit = st.form_submit_button(
                "Crear cuenta",
                type="primary",
                use_container_width=True,
            )

        if submit:
            if not display_name.strip():
                st.error("Escribe un nombre visible o alias.")
            elif len(password) < 8:
                st.error("La contraseña debe tener al menos 8 caracteres.")
            elif password != confirm:
                st.error("Las contraseñas no coinciden.")
            elif age_on_date(birth_date) < 18:
                st.error("El prototipo está diseñado para personas mayores de 18 años.")
            elif not demographic_consent:
                st.error(
                    "Para registrar la fecha de nacimiento y generar KPI demográficos debes aceptar el consentimiento sociodemográfico."
                )
            else:
                try:
                    response = sign_up(
                        email.strip(),
                        password,
                        display_name.strip(),
                        birth_date,
                        gender,
                        demographic_consent,
                    )
                    st.success(response["message"])
                    if response["confirmed"]:
                        st.rerun()
                except Exception as exc:
                    st.error(f"No fue posible crear la cuenta: {exc}")


if not is_logged_in():
    login_screen()
    st.stop()


# =========================================================
# NAVEGACION
# =========================================================

profile = current_profile()
role = current_role()

with st.sidebar:
    st.markdown("## SENZIA")
    st.write(f'**{profile.get("display_name") or st.session_state.auth_email}**')
    st.caption(f"Rol: {role}")

    pages = ["Mi resumen", "Mi historial", "Mi perfil"]
    if role in {"reviewer", "admin"}:
        pages.append("KPI globales")
    if role == "admin":
        pages.append("Usuarios")

    page = st.radio("Menú", pages)
    if st.button("Cerrar sesión", use_container_width=True):
        sign_out()
        st.rerun()

hero(
    "SENZIA",
    "Indicadores de bienestar organizacional",
    "Consulta tendencias personales y métricas académicas agregadas según los permisos de tu perfil.",
)

start_default, end_default = default_range(30)


# =========================================================
# MI RESUMEN
# =========================================================

if page == "Mi resumen":
    st.subheader("Mi resumen")
    col1, col2 = st.columns(2)
    start = col1.date_input("Desde", start_default, max_value=date.today())
    end = col2.date_input("Hasta", end_default, max_value=date.today())

    if start > end:
        st.error("La fecha inicial no puede ser posterior a la final.")
        st.stop()

    data = my_kpis(start, end)
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Conversaciones", data.get("total_sessions", 0))
    with c2:
        kpi_card("Finalizadas", data.get("completed_sessions", 0))
    with c3:
        kpi_card("Tasa de finalización", f'{data.get("completion_rate", 0):.1f}%')

    left, right = st.columns(2)
    with left:
        st.markdown("### Dimensiones conversadas")
        frame = dataframe_from_counts(data.get("dimensions"), "Dimensión", "Conversaciones")
        if frame.empty:
            st.info("No hay dimensiones registradas en el periodo.")
        else:
            st.bar_chart(frame.set_index("Dimensión"))
    with right:
        st.markdown("### Orientaciones")
        frame = dataframe_from_counts(data.get("orientations"), "Orientación", "Conversaciones")
        if frame.empty:
            st.info("No hay orientaciones registradas en el periodo.")
        else:
            st.bar_chart(frame.set_index("Orientación"))


# =========================================================
# HISTORIAL
# =========================================================

elif page == "Mi historial":
    st.subheader("Mi historial")
    rows = my_sessions()
    if not rows:
        st.info("Aún no tienes conversaciones asociadas a esta cuenta.")

    for row in rows:
        raw_result = row.get("results") or {}
        result = raw_result[0] if isinstance(raw_result, list) and raw_result else raw_result
        with st.expander(
            f'{row.get("started_at", "Sin fecha")} · {row.get("status", "sin estado")}'
        ):
            st.write("**Dimensiones:**", ", ".join(result.get("dimensions") or []) or "Sin dimensión")
            st.write("**Frecuencia:**", result.get("frequency") or "Sin registro")
            st.write("**Duración:**", result.get("duration") or "Sin registro")
            st.write("**Orientación:**", result.get("orientation") or "Sin resultado")
            st.caption("Este resumen no constituye un diagnóstico.")


# =========================================================
# PERFIL
# =========================================================

elif page == "Mi perfil":
    st.subheader("Mi perfil")

    stored_birth = profile.get("birth_date")
    try:
        birth_default = date.fromisoformat(stored_birth) if stored_birth else date(1995, 1, 1)
    except ValueError:
        birth_default = date(1995, 1, 1)

    gender_options = [
        "Prefiero no responder",
        "Mujer",
        "Hombre",
        "No binario",
        "Otra identidad",
    ]
    stored_gender = profile.get("gender_identity") or "Prefiero no responder"
    gender_index = gender_options.index(stored_gender) if stored_gender in gender_options else 0

    with st.form("profile_form"):
        display_name = st.text_input(
            "Nombre visible",
            value=profile.get("display_name") or "",
        )
        st.text_input(
            "Correo",
            value=st.session_state.auth_email or "",
            disabled=True,
        )
        st.text_input("Rol", value=role, disabled=True)

        max_birth_date = date(date.today().year - 18, date.today().month, date.today().day)
        birth_date = st.date_input(
            "Fecha de nacimiento",
            value=birth_default,
            min_value=date(1940, 1, 1),
            max_value=max_birth_date,
            format="DD/MM/YYYY",
        )
        gender = st.selectbox("Género", gender_options, index=gender_index)
        demographic_consent = st.checkbox(
            "Autorizo el uso sociodemográfico agregado.",
            value=bool(profile.get("demographic_consent", False)),
        )
        st.caption(f"Edad actual calculada: {age_on_date(birth_date)} años.")
        submit = st.form_submit_button("Guardar cambios", type="primary")

    if submit:
        if not display_name.strip():
            st.error("El nombre visible no puede estar vacío.")
        elif age_on_date(birth_date) < 18:
            st.error("La fecha corresponde a una persona menor de 18 años.")
        else:
            try:
                update_my_profile(
                    display_name.strip(),
                    birth_date,
                    gender,
                    demographic_consent,
                )
                st.success("Perfil actualizado.")
                st.rerun()
            except Exception as exc:
                st.error(f"No fue posible actualizar el perfil: {exc}")


# =========================================================
# KPI GLOBALES Y DEMOGRAFICOS
# =========================================================

elif page == "KPI globales":
    st.subheader("KPI académicos globales")
    st.info(
        "Los filtros demográficos utilizan la edad que tenía la persona cuando ocurrió cada conversación. "
        "Los resultados se ocultan si el segmento tiene menos de 5 usuarios únicos."
    )

    d1, d2, d3, d4 = st.columns(4)
    start = d1.date_input("Desde", start_default, key="admin_start", max_value=date.today())
    end = d2.date_input("Hasta", end_default, key="admin_end", max_value=date.today())
    age_range = d3.selectbox(
        "Rango de edad",
        ["Todos", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
    )
    gender_filter = d4.selectbox(
        "Género",
        ["Todos", "Mujer", "Hombre", "No binario", "Otra identidad", "Prefiero no responder"],
    )

    global_data = admin_kpis(start, end)
    demographic = demographic_kpis(start, end, age_range, gender_filter)

    cols = st.columns(4)
    values = [
        ("Usuarios activos", global_data.get("active_users", 0)),
        ("Conversaciones", global_data.get("total_sessions", 0)),
        ("Finalización", f'{global_data.get("completion_rate", 0):.1f}%'),
        ("Gemini exitoso", f'{global_data.get("gemini_success_rate", 0):.1f}%'),
    ]
    for column, (label, value) in zip(cols, values):
        with column:
            kpi_card(label, value)

    if demographic.get("suppressed"):
        st.warning(
            "El segmento seleccionado tiene menos de 5 usuarios únicos. "
            "SENZIA oculta los resultados para reducir el riesgo de identificación."
        )
    else:
        st.markdown("### Segmento demográfico seleccionado")
        cols = st.columns(3)
        with cols[0]:
            kpi_card("Usuarios únicos", demographic.get("unique_users", 0))
        with cols[1]:
            kpi_card("Conversaciones", demographic.get("total_sessions", 0))
        with cols[2]:
            kpi_card("Finalización", f'{demographic.get("completion_rate", 0):.1f}%')

        left, right = st.columns(2)
        with left:
            st.markdown("#### Dimensiones del segmento")
            frame = dataframe_from_counts(demographic.get("dimensions"), "Dimensión", "Cantidad")
            if not frame.empty:
                st.bar_chart(frame.set_index("Dimensión"))
            else:
                st.info("No hay dimensiones para el segmento.")
        with right:
            st.markdown("#### Orientaciones del segmento")
            frame = dataframe_from_counts(demographic.get("orientations"), "Orientación", "Cantidad")
            if not frame.empty:
                st.bar_chart(frame.set_index("Orientación"))
            else:
                st.info("No hay orientaciones para el segmento.")

    st.markdown("### Aprendizaje supervisado")
    cols = st.columns(4)
    values = [
        ("Pendientes", global_data.get("pending_proposals", 0)),
        ("Aprobadas", global_data.get("approved_proposals", 0)),
        ("Rechazadas", global_data.get("rejected_proposals", 0)),
        ("Sin dimensión", global_data.get("sessions_without_dimension", 0)),
    ]
    for column, (label, value) in zip(cols, values):
        with column:
            kpi_card(label, value)


# =========================================================
# USUARIOS
# =========================================================

elif page == "Usuarios":
    st.subheader("SENZIA Administración")
    users = list_profiles_admin()
    if not users:
        st.info("No hay usuarios registrados.")

    for user in users:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.write(f'**{user.get("display_name") or "Sin nombre"}**')
            col1.caption(
                f'Género: {user.get("gender_identity") or "Sin información"} · '
                f'Fecha de nacimiento: {user.get("birth_date") or "Sin información"}'
            )
            role_value = col2.selectbox(
                "Rol",
                ["participant", "reviewer", "admin"],
                index=["participant", "reviewer", "admin"].index(
                    user.get("role", "participant")
                ),
                key=f'role_{user["id"]}',
            )
            active = col3.checkbox(
                "Activo",
                value=bool(user.get("active", True)),
                key=f'active_{user["id"]}',
            )
            if st.button("Guardar usuario", key=f'save_{user["id"]}'):
                try:
                    update_profile_role_admin(user["id"], role_value, active)
                    st.success("Usuario actualizado.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"No fue posible actualizar el usuario: {exc}")
