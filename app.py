import streamlit as st
import pandas as pd

from src.detector import encontrar_coincidencia
from src.orientacion import calcular_orientacion, construir_resumen

st.set_page_config(
    page_title="Escucha Laboral",
    page_icon="💬",
    layout="centered",
)


@st.cache_data
def cargar_diccionario():
    return pd.read_csv("data/diccionario.csv")


@st.cache_data
def cargar_recomendaciones():
    return pd.read_csv("data/recomendaciones.csv")


def mensaje_asistente(texto):
    st.session_state.mensajes.append({"role": "assistant", "content": texto})


def mensaje_usuario(texto):
    st.session_state.mensajes.append({"role": "user", "content": texto})


def reiniciar_conversacion():
    claves = [
        "mensajes",
        "etapa",
        "dimension",
        "expresion_detectada",
        "respuesta_contexto",
        "frecuencia",
        "duracion",
        "impacto",
        "orientacion",
        "consentimiento",
    ]
    for clave in claves:
        st.session_state.pop(clave, None)
    st.rerun()


def inicializar_estado():
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = [
            {
                "role": "assistant",
                "content": (
                    "Hola. Soy Escucha Laboral, un prototipo académico de orientación "
                    "preventiva. Cuéntame cómo has vivido tu entorno de trabajo durante "
                    "las últimas semanas."
                ),
            }
        ]
    if "etapa" not in st.session_state:
        st.session_state.etapa = "relato"
    if "dimension" not in st.session_state:
        st.session_state.dimension = "situación laboral por aclarar"
    if "expresion_detectada" not in st.session_state:
        st.session_state.expresion_detectada = ""
    if "impacto" not in st.session_state:
        st.session_state.impacto = []


st.title("Escucha Laboral")
st.caption("MVP académico de orientación preventiva - Versión 2")
st.warning(
    "Este prototipo no realiza diagnósticos, no sustituye la Batería de Riesgo "
    "Psicosocial y no reemplaza la atención de profesionales de Seguridad y Salud "
    "en el Trabajo, Gestión Humana o salud mental."
)

with st.expander("Antes de comenzar: alcance y tratamiento de la información"):
    st.markdown(
        """
- La participación en esta demostración es voluntaria.
- No escribas nombres, documentos, teléfonos, correos ni datos de una empresa real.
- La versión académica no envía respuestas a Recursos Humanos.
- Las orientaciones son experimentales y no equivalen a una medición oficial.
- Para esta demostración se recomienda usar situaciones ficticias o anonimizadas.
        """
    )

consentimiento = st.checkbox(
    "Comprendo el alcance y acepto participar voluntariamente en esta demostración.",
    key="consentimiento",
)

if consentimiento:
    inicializar_estado()
    diccionario = cargar_diccionario()
    recomendaciones = cargar_recomendaciones()

    col1, col2 = st.columns([4, 1])
    with col2:
        st.button("Reiniciar", on_click=reiniciar_conversacion, use_container_width=True)

    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"]):
            st.write(mensaje["content"])

    etapa = st.session_state.etapa

    if etapa in {"relato", "contexto"}:
        placeholder = (
            "Escribe cómo has vivido tu entorno laboral..."
            if etapa == "relato"
            else "Responde la pregunta de aclaración..."
        )
        entrada = st.chat_input(placeholder, max_chars=1200)

        if entrada:
            entrada = entrada.strip()
            mensaje_usuario(entrada)

            if etapa == "relato":
                coincidencia = encontrar_coincidencia(entrada, diccionario)

                if coincidencia is not None:
                    st.session_state.dimension = str(coincidencia["dimension_probable"])
                    st.session_state.expresion_detectada = str(coincidencia["expresion"])
                    pregunta = str(coincidencia["pregunta_aclaratoria"])
                    respuesta = (
                        "Gracias por compartirlo. Antes de sacar conclusiones, quisiera "
                        f"comprender mejor la situación. {pregunta}"
                    )
                else:
                    st.session_state.dimension = "situación laboral por aclarar"
                    respuesta = (
                        "Gracias por contarlo. ¿Qué situación concreta del trabajo está "
                        "influyendo más en cómo te sientes?"
                    )

                mensaje_asistente(respuesta)
                st.session_state.etapa = "contexto"

            else:
                st.session_state.respuesta_contexto = entrada
                mensaje_asistente(
                    "Gracias. Ahora necesito conocer la frecuencia con la que ocurre."
                )
                st.session_state.etapa = "frecuencia"

            st.rerun()

    elif etapa == "frecuencia":
        frecuencia = st.radio(
            "¿Con qué frecuencia ocurre esta situación?",
            [
                "Ocurrió una vez",
                "Sucede ocasionalmente",
                "Sucede varias veces por semana",
                "Sucede casi todos los días",
            ],
            index=None,
        )
        if st.button("Guardar frecuencia", disabled=frecuencia is None):
            st.session_state.frecuencia = frecuencia
            mensaje_usuario(f"Frecuencia: {frecuencia}")
            mensaje_asistente("¿Desde cuándo ocurre esta situación?")
            st.session_state.etapa = "duracion"
            st.rerun()

    elif etapa == "duracion":
        duracion = st.radio(
            "¿Desde cuándo ocurre?",
            [
                "Desde hace pocos días",
                "Desde hace varias semanas",
                "Desde hace algunos meses",
                "Desde hace más de seis meses",
            ],
            index=None,
        )
        if st.button("Guardar duración", disabled=duracion is None):
            st.session_state.duracion = duracion
            mensaje_usuario(f"Duración: {duracion}")
            mensaje_asistente(
                "Para completar la orientación, selecciona los aspectos que se han visto afectados."
            )
            st.session_state.etapa = "impacto"
            st.rerun()

    elif etapa == "impacto":
        opciones_impacto = [
            "Descanso",
            "Concentración",
            "Motivación",
            "Relaciones laborales",
            "Vida personal",
            "Cumplimiento de tareas",
            "Ninguno de los anteriores",
        ]
        impacto = st.multiselect(
            "¿Qué aspectos se han visto afectados?",
            opciones_impacto,
        )
        seleccion_invalida = (
            "Ninguno de los anteriores" in impacto and len(impacto) > 1
        )
        if seleccion_invalida:
            st.error(
                "Selecciona 'Ninguno de los anteriores' solo, o elige los aspectos afectados."
            )

        if st.button(
            "Generar orientación",
            disabled=(not impacto or seleccion_invalida),
        ):
            st.session_state.impacto = impacto
            mensaje_usuario("Impacto: " + ", ".join(impacto))

            nivel, puntaje = calcular_orientacion(
                st.session_state.frecuencia,
                st.session_state.duracion,
                impacto,
            )
            st.session_state.orientacion = nivel

            resumen = construir_resumen(
                dimension=st.session_state.dimension,
                frecuencia=st.session_state.frecuencia,
                duracion=st.session_state.duracion,
                impacto=impacto,
                nivel=nivel,
                recomendaciones_df=recomendaciones,
            )
            mensaje_asistente(resumen)
            st.session_state.etapa = "resultado"
            st.rerun()

    elif etapa == "resultado":
        st.success("La conversación preventiva ha finalizado.")
        st.info(
            "La clasificación mostrada es una regla experimental del prototipo y no "
            "una calificación oficial de riesgo psicosocial."
        )
        st.button(
            "Iniciar una nueva conversación",
            on_click=reiniciar_conversacion,
            type="primary",
        )

else:
    st.info("Marca la casilla de consentimiento para iniciar la demostración.")
