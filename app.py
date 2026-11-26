import base64
from pathlib import Path

import pandas as pd
import streamlit as st

from src.anonymizer import anonimizar
from src.ai_budget import MAX_CALLS_PER_SESSION
from src.gemini import disponible as ia_disponible, analizar
from src.local import (
    norm,
    relacion,
    detectar,
    frecuencia,
    duracion,
    impactos,
    detectar_bienestar_positivo,
    detectar_condicion_desfavorable,
)
from src.messages import (
    BIENVENIDA,
    SIN_INDICADORES,
    ACOMPANAMIENTO_GENERAL,
    ACOMPANAMIENTO_RELACIONES,
    INFORMACION_INSUFICIENTE,
    BIENESTAR_POSITIVO,
    PREGUNTA_BIENESTAR,
)
from src.orientation import calcular
from src.safety import detectar_prioridad, PRIORIDAD
from src.emotional_support import detectar_conceptos, ayudas_para, formatear_ayuda
from src.emergency_ui import mostrar_botones_emergencia
from src.storage import (
    configurado,
    crear_sesion,
    guardar_mensaje,
    guardar_resultado,
    crear_propuesta_supervisada,
    diccionario_activo,
    propuestas_pendientes,
    aprobar_propuesta,
    rechazar_propuesta,
)


# =========================================================
# CONFIGURACION GENERAL
# =========================================================

ZIA = "assets/zia.png"
HUMAN = "assets/persona.png"
VERSION = "7.0-senzia"

st.set_page_config(
    page_title="SENZIA Conversa",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =========================================================
# FUNCIONES CONVERSACIONALES INTEGRADAS
# =========================================================

def interpretar_relacion_local(texto):
    return relacion(texto)


def analizar_contexto_local(texto, diccionario):
    return detectar(texto, diccionario)


def interpretar_frecuencia_local(texto):
    return frecuencia(texto)


def interpretar_duracion_local(texto):
    return duracion(texto)


def interpretar_impactos_local(texto):
    return impactos(texto)


def es_correccion(texto):
    texto_normalizado = norm(texto)
    expresiones = [
        "no es eso",
        "no quise decir",
        "entendiste mal",
        "quiero corregir",
        "eso no",
        "me refiero a",
        "no representa",
    ]
    return any(expresion in texto_normalizado for expresion in expresiones)


def texto_es_suficiente(texto):
    texto_normalizado = norm(texto)
    palabras = texto_normalizado.split()
    marcadores = [
        "persigue",
        "hostiga",
        "acosa",
        "grita",
        "humilla",
        "insinua",
        "toca",
        "horario",
        "jornada",
        "trabajo",
        "tareas",
        "jefe",
        "jefa",
        "supervisor",
        "coordinador",
        "comentarios",
        "amenaza",
        "ignora",
        "excluye",
        "carga",
        "turno",
        "comodin",
        "achantado",
        "achantada",
    ]
    return len(palabras) >= 6 and any(
        marcador in texto_normalizado for marcador in marcadores
    )


def construir_pregunta_contextual(analisis_ia, dimensiones):
    if analisis_ia and analisis_ia.pregunta:
        return analisis_ia.pregunta
    if "relaciones y liderazgo" in dimensiones:
        return "¿Qué conducta ocurrió, cuándo suele pasar y qué efecto ha tenido en ti?"
    if "carga laboral" in dimensiones:
        return "¿Qué tareas o plazos concretos están generando esa presión?"
    if "jornada y desconexión" in dimensiones:
        return "¿Qué ocurre con tus horarios, pausas o tiempo fuera de la jornada?"
    return "¿Qué ocurrió exactamente y en qué contexto suele suceder?"


def expresion_para_propuesta(texto_anonimo, analisis_ia, hubo_coincidencia_local):
    if hubo_coincidencia_local or not analisis_ia or not analisis_ia.dimensiones:
        return None
    expresion = (analisis_ia.expresion_nueva or texto_anonimo).strip()
    return expresion[:220] if len(expresion) >= 4 else None


CONTEXT_OBJECTIVE = """
Analiza el relato laboral completo. Identifica hasta tres dimensiones
permitidas sin diagnosticar ni confirmar acoso. Redacta UNA sola pregunta
de profundización que use detalles del mensaje. No preguntes
'¿representa lo que quisiste expresar?'. Si la frase es nueva o coloquial,
devuelve en expresion_nueva una versión breve y reutilizable.
"""


# =========================================================
# ESTILOS SENZIA
# =========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --senzia-bg: #070D1A;
        --senzia-bg-soft: #0C1426;
        --senzia-card: #101B31;
        --senzia-card-light: #14213A;
        --senzia-text: #F2F5FF;
        --senzia-muted: #A7B2C9;
        --senzia-cyan: #20D5F5;
        --senzia-blue: #3C8DFF;
        --senzia-purple: #8067FF;
        --senzia-border: #21365A;
        --senzia-success: #70D6A0;
        --senzia-warning: #F3C969;
    }

    html, body, [class*="css"] {
        font-family: "Inter", sans-serif;
    }

    .stApp {
        color: var(--senzia-text);
        background:
            radial-gradient(circle at 84% 12%, rgba(60,141,255,.13), transparent 25%),
            radial-gradient(circle at 10% 70%, rgba(32,213,245,.08), transparent 30%),
            linear-gradient(180deg, #070D1A 0%, #080F1E 100%);
    }

    .block-container {
        max-width: 930px;
        padding-top: 1.1rem;
        padding-bottom: 7rem;
    }

    header[data-testid="stHeader"] { background: transparent; }

    [data-testid="stSidebar"] {
        background: #080F1E;
        border-right: 1px solid var(--senzia-border);
    }

    [data-testid="stSidebar"] * { color: var(--senzia-text); }

    .senzia-hero {
        position: relative;
        overflow: hidden;
        padding: 26px;
        margin-bottom: 16px;
        border: 1px solid var(--senzia-border);
        border-radius: 26px;
        background: linear-gradient(135deg, rgba(16,27,49,.98), rgba(11,20,40,.98));
        box-shadow: 0 24px 70px rgba(0,0,0,.25), inset 0 1px 0 rgba(255,255,255,.04);
    }

    .senzia-hero::before {
        content: "";
        position: absolute;
        width: 280px;
        height: 280px;
        right: -90px;
        top: -120px;
        border-radius: 50%;
        background: rgba(32,213,245,.12);
        filter: blur(12px);
    }

    .senzia-hero::after {
        content: "";
        position: absolute;
        width: 240px;
        height: 240px;
        left: -100px;
        bottom: -180px;
        border-radius: 50%;
        background: rgba(128,103,255,.12);
        filter: blur(18px);
    }

    .senzia-hero-content {
        position: relative;
        z-index: 2;
        display: grid;
        grid-template-columns: 1fr 190px;
        align-items: center;
        gap: 24px;
    }

    .senzia-eyebrow {
        display: inline-flex;
        width: fit-content;
        margin-bottom: 12px;
        padding: 7px 13px;
        border: 1px solid rgba(32,213,245,.22);
        border-radius: 999px;
        color: var(--senzia-cyan);
        background: rgba(32,213,245,.07);
        font-size: .79rem;
        font-weight: 600;
        letter-spacing: .02em;
    }

    .senzia-brand {
        margin: 0;
        color: var(--senzia-text);
        font-size: 2.3rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: .06em;
    }

    .senzia-module {
        margin-top: 8px;
        background: linear-gradient(90deg, var(--senzia-cyan), var(--senzia-purple));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        font-size: 1.08rem;
        font-weight: 750;
    }

    .senzia-description {
        max-width: 600px;
        margin: 13px 0 0;
        color: var(--senzia-muted);
        font-size: .94rem;
        line-height: 1.62;
    }

    .senzia-avatar-shell {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 170px;
        border: 1px solid rgba(60,141,255,.3);
        border-radius: 24px;
        background: radial-gradient(circle, rgba(32,213,245,.16), rgba(128,103,255,.05) 55%, transparent 70%);
    }

    .senzia-avatar-shell img {
        width: 142px;
        height: 142px;
        object-fit: cover;
        border: 2px solid rgba(32,213,245,.55);
        border-radius: 50%;
        box-shadow: 0 0 28px rgba(32,213,245,.22), 0 0 50px rgba(128,103,255,.15);
        animation: ziaFloat 4s ease-in-out infinite;
    }

    @keyframes ziaFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-7px); }
    }

    .senzia-info {
        margin: 13px 0;
        padding: 16px 18px;
        border: 1px solid var(--senzia-border);
        border-radius: 18px;
        color: var(--senzia-muted);
        background: rgba(16,27,49,.88);
        line-height: 1.55;
    }

    .senzia-info strong { color: var(--senzia-text); }

    .consent-note {
        margin: -4px 0 12px 38px;
        color: var(--senzia-muted);
        font-size: .82rem;
        line-height: 1.42;
    }

    [data-testid="stChatMessage"] {
        padding: 14px 16px;
        margin-bottom: 10px;
        border: 1px solid var(--senzia-border);
        border-radius: 20px;
        color: var(--senzia-text);
        background: rgba(16,27,49,.93);
        box-shadow: none;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        margin-left: 9%;
        border-color: rgba(32,213,245,.26);
        background: linear-gradient(135deg, rgba(23,55,81,.96), rgba(20,43,69,.96));
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        color: var(--senzia-text);
        line-height: 1.58;
    }

    [data-testid="stChatInput"] {
        border: 1px solid var(--senzia-border);
        border-radius: 18px;
        background: var(--senzia-card);
        box-shadow: 0 18px 50px rgba(0,0,0,.24);
    }

    [data-testid="stChatInput"] textarea {
        color: var(--senzia-text);
        background: transparent;
    }

    [data-testid="stChatInput"] textarea::placeholder { color: #74839F; }

    [data-testid="stChatInputSubmitButton"] {
        color: #07101A;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--senzia-cyan), var(--senzia-purple));
    }

    .stButton > button {
        min-height: 42px;
        color: var(--senzia-text);
        border: 1px solid var(--senzia-border);
        border-radius: 14px;
        background: var(--senzia-card);
        font-weight: 650;
    }

    .stButton > button:hover {
        color: white;
        border-color: var(--senzia-cyan);
        box-shadow: 0 0 20px rgba(32,213,245,.15);
    }

    .stButton > button[kind="primary"] {
        color: #07101A;
        border: none;
        background: linear-gradient(135deg, var(--senzia-cyan), var(--senzia-purple));
    }

    [data-testid="stExpander"] {
        border: 1px solid var(--senzia-border);
        border-radius: 18px;
        background: rgba(16,27,49,.83);
    }

    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stDateInput"] input {
        color: var(--senzia-text);
        border-color: var(--senzia-border);
        background: var(--senzia-card);
    }

    .senzia-status {
        display: inline-flex;
        gap: 7px;
        padding: 6px 11px;
        border: 1px solid rgba(32,213,245,.2);
        border-radius: 999px;
        color: var(--senzia-cyan);
        background: rgba(32,213,245,.07);
        font-size: .76rem;
        font-weight: 600;
    }

    @media (max-width: 720px) {
        .block-container { padding: .75rem .8rem 6rem; }
        .senzia-hero { padding: 18px; }
        .senzia-hero-content { grid-template-columns: 1fr; }
        .senzia-avatar-shell { display: none; }
        .senzia-brand { font-size: 1.8rem; }
        [data-testid="stChatMessage"] { margin-left: 0 !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# CARGA DE RECURSOS Y CABECERA
# =========================================================

def image_b64(path):
    file_path = Path(path)
    if not file_path.exists():
        return ""
    return base64.b64encode(file_path.read_bytes()).decode()


zia_b64 = image_b64(ZIA)
zia_visual = (
    f'<img src="data:image/png;base64,{zia_b64}" alt="Avatar digital de Zia">'
    if zia_b64
    else '<div style="font-size:72px">✦</div>'
)

st.markdown(
    f"""
    <section class="senzia-hero">
        <div class="senzia-hero-content">
            <div>
                <div class="senzia-eyebrow">
                    Inteligencia · Bienestar · Transformación
                </div>
                <h1 class="senzia-brand">SENZIA</h1>
                <div class="senzia-module">
                    Conversación preventiva sobre bienestar laboral
                </div>
                <p class="senzia-description">
                    Escribe con tus propias palabras lo que estás viviendo.
                    Zia te ayudará a organizar la situación, comprender si
                    existen condiciones laborales relacionadas y recibir
                    una orientación preventiva.
                </p>
            </div>
            <div class="senzia-avatar-shell">{zia_visual}</div>
        </div>
    </section>

    <div class="senzia-info">
        <strong>¿Qué puedes hacer aquí?</strong><br>
        Este es un espacio académico de conversación. Puedes contar una
        situación de tu entorno laboral, responder preguntas de contexto
        y recibir una orientación preventiva. SENZIA no realiza
        diagnósticos ni reemplaza la atención de profesionales.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DATOS Y ESTADO
# =========================================================

@st.cache_data(ttl=60)
def cargar_diccionario():
    if configurado():
        try:
            rows = diccionario_activo()
            if rows:
                return pd.DataFrame(
                    [
                        {
                            "expresion": row["expression"],
                            "variantes": row["variants"],
                            "dimension": row["dimension"],
                            "pregunta": row["question"],
                        }
                        for row in rows
                    ]
                )
        except Exception:
            pass
    return pd.read_csv("data/diccionario_respaldo.csv")


def add(role, text, used_ai=False):
    st.session_state.msg.append({"role": role, "content": text})
    if st.session_state.get("db_session") and st.session_state.get("autoriza_guardado"):
        try:
            guardar_mensaje(
                {
                    "session_id": st.session_state.db_session,
                    "role": role,
                    "anonymized_text": anonimizar(text),
                    "stage": st.session_state.etapa,
                    "used_ai": used_ai,
                    "sequence_no": len(st.session_state.msg),
                }
            )
        except Exception as exc:
            st.session_state.storage_error = str(exc)


def init():
    defaults = {
        "etapa": "relato",
        "msg": [],
        "dims": [],
        "frec": None,
        "dur": None,
        "imps": [],
        "db_session": None,
        "prioridad": False,
        "gemini_calls": 0,
        "storage_error": None,
        "context_attempts": 0,
        "gemini_budget_error": None,
        "consentimientos_confirmados": False,
        "contexto_ia_realizado": False,
        "contexto_profundizado": False,
        "emociones_detectadas": [],
        "hay_condicion_desfavorable": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if not st.session_state.msg:
        add("assistant", BIENVENIDA)


def reset():
    for key in list(st.session_state.keys()):
        st.session_state.pop(key, None)
    st.rerun()


def review_panel():
    st.subheader("SENZIA Revisión")
    st.caption(
        "Las propuestas permanecen pendientes hasta que una persona "
        "autorizada las aprueba o rechaza."
    )
    password = st.text_input("Contraseña de revisión", type="password")
    if not password or password != st.secrets.get("REVIEW_PASSWORD", ""):
        st.info("Ingresa la contraseña de revisión.")
        return
    if not configurado(admin=True):
        st.error("Falta la clave privada de Supabase.")
        return

    proposals = propuestas_pendientes()
    st.metric("Propuestas pendientes", len(proposals))
    for proposal in proposals:
        with st.container(border=True):
            st.write(f"**{proposal['expression']}**")
            st.write(proposal.get("dimensions", []))
            st.caption(str(proposal.get("evidence", "")))
            dim = st.text_input(
                "Dimensión",
                value=(proposal.get("dimensions") or [""])[0],
                key=f"d{proposal['id']}",
            )
            variants = st.text_input(
                "Variantes con |", key=f"v{proposal['id']}"
            )
            question = st.text_input(
                "Pregunta",
                value="¿Puedes contarme un ejemplo concreto?",
                key=f"q{proposal['id']}",
            )
            col1, col2 = st.columns(2)
            if col1.button("Aprobar", key=f"a{proposal['id']}"):
                aprobar_propuesta(
                    proposal["id"],
                    proposal["expression"],
                    variants,
                    dim,
                    question,
                )
                st.cache_data.clear()
                st.rerun()
            if col2.button("Rechazar", key=f"r{proposal['id']}"):
                rechazar_propuesta(proposal["id"])
                st.rerun()


init()
df = cargar_diccionario()

mode = st.sidebar.radio(
    "SENZIA",
    ["SENZIA Conversa", "SENZIA Revisión"],
)
if mode == "SENZIA Revisión":
    review_panel()
    st.stop()


# =========================================================
# CONSENTIMIENTOS
# =========================================================

with st.expander(
    "Participación y uso académico",
    expanded=not st.session_state.consentimientos_confirmados,
):
    st.markdown(
        "**Revisa cada opción.** Solo la participación es obligatoria; "
        "las demás son opcionales."
    )
    st.checkbox("Acepto participar voluntariamente.", key="participa")
    st.markdown(
        '<div class="consent-note">Permite iniciar. Puedes detenerte o reiniciar.</div>',
        unsafe_allow_html=True,
    )
    st.checkbox(
        "Autorizo guardar una copia anonimizada del chat.",
        key="autoriza_guardado",
        disabled=not configurado(),
    )
    st.markdown(
        '<div class="consent-note">Guarda una copia académica con reemplazo básico de correos, teléfonos, URL y algunos documentos.</div>',
        unsafe_allow_html=True,
    )
    st.checkbox(
        "Autorizo enviar fragmentos anonimizados a Gemini.",
        key="autoriza_ia",
        disabled=not ia_disponible(),
    )
    st.markdown(
        '<div class="consent-note">Gemini ayuda a interpretar lenguaje abierto. Máximo 3 llamadas por conversación.</div>',
        unsafe_allow_html=True,
    )
    st.checkbox(
        "Autorizo proponer expresiones anonimizadas para mejorar el diccionario.",
        key="autoriza_aprendizaje",
        disabled=not configurado(),
    )
    st.markdown(
        '<div class="consent-note">La propuesta queda pendiente y requiere aprobación humana.</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "Revisé las opciones y deseo iniciar",
        type="primary",
        use_container_width=True,
    ):
        if not st.session_state.participa:
            st.error("Debes aceptar la participación voluntaria.")
        else:
            st.session_state.consentimientos_confirmados = True
            st.rerun()

if not st.session_state.consentimientos_confirmados:
    st.stop()

if st.session_state.autoriza_guardado and not st.session_state.db_session:
    try:
        response = crear_sesion(
            {
                "app_version": VERSION,
                "consent_store": True,
                "consent_ai": bool(st.session_state.autoriza_ia),
                "consent_learning": bool(st.session_state.autoriza_aprendizaje),
            }
        )
        st.session_state.db_session = response["id"]
    except Exception as exc:
        st.error(f"No fue posible iniciar el guardado: {exc}")


# =========================================================
# CHAT
# =========================================================

col1, col2 = st.columns([5, 1])
with col1:
    status_data = "activos" if st.session_state.db_session else "temporales"
    st.markdown(
        f"""
        <span class="senzia-status">
            Etapa: {st.session_state.etapa}
            · IA {st.session_state.gemini_calls}/{MAX_CALLS_PER_SESSION}
            · Datos {status_data}
        </span>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.button("Reiniciar", on_click=reset)

for message in st.session_state.msg:
    avatar = ZIA if message["role"] == "assistant" and Path(ZIA).exists() else (
        HUMAN if message["role"] == "user" and Path(HUMAN).exists() else None
    )
    with st.chat_message(message["role"], avatar=avatar):
        st.write(message["content"])

if st.session_state.etapa == "prioridad":
    st.error(
        "Si existe peligro inmediato o una acción en curso, abre emergencias 123. "
        "Para orientación en salud mental, abre la Línea 106."
    )
    mostrar_botones_emergencia()
    st.info(
        "Busca compañía de una persona de confianza y evita quedarte a solas "
        "mientras recibes apoyo, si hacerlo es seguro."
    )

if st.session_state.etapa == "fin":
    st.success(
        "La conversación ha finalizado. La orientación queda visible; "
        "no necesitas reiniciar para leerla."
    )

user_text = None if st.session_state.etapa == "fin" else st.chat_input(
    "Cuéntame con tus propias palabras..."
)

if user_text:
    add("user", user_text)

    if detectar_prioridad(user_text):
        st.session_state.prioridad = True
        add(
            "assistant",
            PRIORIDAD
            + "\n\nNo necesitas reiniciar. Los botones de llamada permanecerán "
            "disponibles debajo de la conversación.",
        )
        st.session_state.etapa = "prioridad"
        st.rerun()

    nuevos_conceptos = detectar_conceptos(user_text)
    st.session_state.emociones_detectadas = list(
        dict.fromkeys(
            st.session_state.emociones_detectadas + nuevos_conceptos
        )
    )

    etapa = st.session_state.etapa
    texto_anonimo = anonimizar(user_text)

    if etapa == "relato":
        bienestar = detectar_bienestar_positivo(user_text)
        desfavorable = detectar_condicion_desfavorable(user_text)
        st.session_state.hay_condicion_desfavorable = desfavorable

        if bienestar and not desfavorable:
            add("assistant", PREGUNTA_BIENESTAR)
            st.session_state.etapa = "bienestar_contexto"
        else:
            add(
                "assistant",
                "Gracias por contármelo. ¿Se relaciona con el trabajo, "
                "con algo personal, con ambas cosas o aún no lo tienes claro?",
            )
            st.session_state.etapa = "relacion"

    elif etapa == "bienestar_contexto":
        desfavorable = detectar_condicion_desfavorable(user_text)
        st.session_state.hay_condicion_desfavorable = desfavorable
        if desfavorable:
            add(
                "assistant",
                "Gracias por aclararlo. Aunque en general te sientes bien, "
                "mencionaste una situación laboral que podría ser importante "
                "explorar. ¿Qué está ocurriendo concretamente?",
            )
            st.session_state.etapa = "contexto"
        else:
            add("assistant", BIENESTAR_POSITIVO)
            st.session_state.etapa = "fin"

    elif etapa == "relacion":
        relationship = interpretar_relacion_local(user_text)
        ia = None
        if (
            relationship is None
            and ia_disponible()
            and st.session_state.autoriza_ia
        ):
            ia = analizar(
                texto_anonimo,
                etapa,
                {"objetivo": "relación"},
                st.session_state.db_session,
            )
            relationship = ia.relacion if ia else None

        if relationship == "personal":
            add(
                "assistant",
                "Gracias por compartirlo. Con lo conversado no identificamos "
                "elementos suficientes para relacionarlo con factores laborales. "
                "Puedes buscar apoyo adecuado para otros aspectos de tu vida. 💚",
                bool(ia),
            )
            st.session_state.etapa = "fin"
        elif relationship == "incierta":
            add(
                "assistant",
                "Está bien no tenerlo claro. ¿Qué estaba ocurriendo justo antes "
                "y en qué contexto suele suceder?",
                bool(ia),
            )
            st.session_state.etapa = "contexto"
        else:
            st.session_state.hay_condicion_desfavorable = True
            add(
                "assistant",
                "¿Qué situación concreta del trabajo está influyendo? "
                "Puedes describir tareas, horarios, trato, cambios o relaciones, "
                "sin incluir nombres.",
                bool(ia),
            )
            st.session_state.etapa = "contexto"

    elif etapa == "contexto":
        local_matches = analizar_contexto_local(texto_anonimo, df)
        local_dimensions = [item["dimension"] for item in local_matches]
        ia = None

        if (
            ia_disponible()
            and st.session_state.autoriza_ia
            and not st.session_state.contexto_ia_realizado
        ):
            ia = analizar(
                texto_anonimo,
                etapa,
                {
                    "objetivo": CONTEXT_OBJECTIVE,
                    "dims_locales": local_dimensions,
                    "dims_previas": st.session_state.dims,
                },
                st.session_state.db_session,
            )
            st.session_state.contexto_ia_realizado = True

        ia_dimensions = ia.dimensiones if ia else []
        dimensions = list(
            dict.fromkeys(
                st.session_state.dims + local_dimensions + ia_dimensions
            )
        )
        st.session_state.dims = dimensions

        proposal = expresion_para_propuesta(
            texto_anonimo,
            ia,
            bool(local_matches),
        )
        if (
            st.session_state.autoriza_aprendizaje
            and proposal
            and st.session_state.db_session
        ):
            try:
                crear_propuesta_supervisada(
                    {
                        "session_id": st.session_state.db_session,
                        "expression": proposal,
                        "dimensions": ia_dimensions,
                        "evidence": texto_anonimo,
                    }
                )
            except Exception as exc:
                st.session_state.storage_error = str(exc)

        if dimensions and not st.session_state.contexto_profundizado:
            question = construir_pregunta_contextual(ia, dimensions)
            add(
                "assistant",
                f"Gracias por explicarlo. Lo que compartes puede relacionarse "
                f"provisionalmente con **{', '.join(dimensions)}**; esto no "
                f"confirma acoso ni una conclusión legal.\n\n{question}",
                bool(ia),
            )
            st.session_state.contexto_profundizado = True
        elif dimensions and st.session_state.contexto_profundizado:
            add(
                "assistant",
                "Gracias por ampliar la situación. ¿Con qué frecuencia ocurre?",
            )
            st.session_state.etapa = "frecuencia"
        else:
            st.session_state.context_attempts += 1
            if texto_es_suficiente(texto_anonimo):
                add(
                    "assistant",
                    "Gracias por describir la situación. Continuemos sin asignar "
                    "una categoría por ahora. ¿Con qué frecuencia ocurre?",
                )
                st.session_state.etapa = "frecuencia"
            elif st.session_state.context_attempts == 1:
                add(
                    "assistant",
                    "¿Qué ocurrió exactamente, cuándo suele pasar y qué efecto "
                    "ha tenido en ti?",
                    bool(ia),
                )
            elif st.session_state.context_attempts == 2:
                add(
                    "assistant",
                    "Puedes contar un último ejemplo concreto o escribir "
                    "**finalizar**. No es necesario usar palabras técnicas.",
                )
            else:
                add("assistant", INFORMACION_INSUFICIENTE)
                st.session_state.etapa = "fin"

    elif etapa == "frecuencia":
        if es_correccion(user_text):
            st.session_state.dims = []
            st.session_state.contexto_ia_realizado = False
            st.session_state.contexto_profundizado = False
            add("assistant", "Claro. Cuéntame cómo describirías mejor la situación.")
            st.session_state.etapa = "contexto"
        else:
            value = interpretar_frecuencia_local(user_text)
            ia = None
            if not value and ia_disponible() and st.session_state.autoriza_ia:
                ia = analizar(
                    texto_anonimo,
                    etapa,
                    {"objetivo": "frecuencia"},
                    st.session_state.db_session,
                )
                value = ia.frecuencia if ia else None
            if value:
                st.session_state.frec = value
                add("assistant", "¿Desde cuándo ocurre?", bool(ia))
                st.session_state.etapa = "duracion"
            else:
                add(
                    "assistant",
                    "¿Ocurrió una vez, ocasionalmente, varias veces por semana "
                    "o casi todos los días?",
                )

    elif etapa == "duracion":
        value = interpretar_duracion_local(user_text)
        ia = None
        if not value and ia_disponible() and st.session_state.autoriza_ia:
            ia = analizar(
                texto_anonimo,
                etapa,
                {"objetivo": "duración"},
                st.session_state.db_session,
            )
            value = ia.duracion if ia else None
        if value:
            st.session_state.dur = value
            add("assistant", "¿Cómo te ha afectado?", bool(ia))
            st.session_state.etapa = "impacto"
        else:
            add(
                "assistant",
                "¿Desde hace días, semanas, meses o más de seis meses?",
            )

    elif etapa == "impacto":
        value = interpretar_impactos_local(user_text)
        ia = None
        no_impact = any(
            expression in norm(user_text)
            for expression in [
                "no me afecta",
                "ninguno",
                "estoy bien",
                "me siento bien",
            ]
        )
        if (
            not value
            and not no_impact
            and ia_disponible()
            and st.session_state.autoriza_ia
        ):
            ia = analizar(
                texto_anonimo,
                etapa,
                {"objetivo": "impactos explícitos"},
                st.session_state.db_session,
            )
            value = ia.impactos if ia else []

        st.session_state.imps = value
        result = calcular(
            st.session_state.frec,
            st.session_state.dur,
            value,
            hay_condicion_desfavorable=(
                st.session_state.hay_condicion_desfavorable
                or bool(st.session_state.dims)
            ),
        )

        if result["tipo"] == "bienestar_positivo":
            final_message = BIENESTAR_POSITIVO
        elif result["tipo"] == "sin_indicadores":
            final_message = SIN_INDICADORES
        elif not st.session_state.dims:
            final_message = INFORMACION_INSUFICIENTE
        elif any(
            dimension in st.session_state.dims
            for dimension in [
                "relaciones y liderazgo",
                "relaciones laborales",
            ]
        ):
            final_message = ACOMPANAMIENTO_RELACIONES
        else:
            final_message = ACOMPANAMIENTO_GENERAL

        add("assistant", final_message, bool(ia))

        if result["tipo"] != "bienestar_positivo":
            for support in ayudas_para(
                st.session_state.emociones_detectadas,
                maximo=2,
            ):
                add("assistant", formatear_ayuda(support))

        st.session_state.etapa = "fin"

        if st.session_state.db_session:
            try:
                guardar_resultado(
                    {
                        "session_id": st.session_state.db_session,
                        "relationship": "laboral",
                        "dimensions": st.session_state.dims,
                        "frequency": st.session_state.frec,
                        "duration": st.session_state.dur,
                        "impacts": value,
                        "orientation": result["tipo"],
                        "rule_version": result["version"],
                    }
                )
            except Exception as exc:
                st.session_state.storage_error = str(exc)

    elif etapa == "prioridad":
        add(
            "assistant",
            "Los botones de Línea 106 y emergencias 123 permanecen disponibles. "
            "Si puedes, busca a una persona de confianza para que te acompañe "
            "mientras accedes a ayuda.",
        )

    st.rerun()
