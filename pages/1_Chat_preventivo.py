import uuid
import pandas as pd
import streamlit as st
from src.detector import detectar_coincidencias
from src.orientacion import calcular_orientacion, recomendacion_para
from src.storage import guardar_resultado

st.set_page_config(page_title="Chat preventivo", page_icon="💬")

@st.cache_data
def cargar_datos():
    return pd.read_csv("data/diccionario.csv"), pd.read_csv("data/recomendaciones.csv")

def iniciar():
    defaults = {
        "v3_etapa": "relato", "v3_mensajes": [], "v3_hallazgos": [],
        "v3_dimensiones": [], "v3_sesion": str(uuid.uuid4()), "v3_feedback": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if not st.session_state.v3_mensajes:
        st.session_state.v3_mensajes.append({"role":"assistant","content":"Cuéntame cómo has vivido tu entorno de trabajo durante las últimas semanas."})

def agregar(role, content):
    st.session_state.v3_mensajes.append({"role": role, "content": content})

def reiniciar():
    for k in list(st.session_state.keys()):
        if k.startswith("v3_"):
            del st.session_state[k]
    st.rerun()

st.title("Chat preventivo V3")
st.warning("No escribas nombres, documentos, teléfonos, correos ni datos de una empresa real.")
consentimiento = st.checkbox("Comprendo el alcance y acepto participar voluntariamente.")
if not consentimiento:
    st.stop()

iniciar()
diccionario, recomendaciones = cargar_datos()
st.button("Reiniciar conversación", on_click=reiniciar)

for m in st.session_state.v3_mensajes:
    with st.chat_message(m["role"]):
        st.write(m["content"])

etapa = st.session_state.v3_etapa
if etapa in {"relato", "aclaracion"}:
    entrada = st.chat_input("Escribe tu respuesta...", max_chars=1200)
    if entrada:
        agregar("user", entrada)
        if etapa == "relato":
            hallazgos = detectar_coincidencias(entrada, diccionario)
            st.session_state.v3_hallazgos = hallazgos
            if hallazgos:
                dims = [h["dimension"] for h in hallazgos]
                st.session_state.v3_dimensiones = dims
                detalle = ", ".join(f"{h['dimension']} ({h['similitud']}%)" for h in hallazgos)
                pregunta = hallazgos[0]["pregunta"]
                agregar("assistant", f"Identifiqué señales provisionales relacionadas con: {detalle}. Antes de concluir: {pregunta}")
            else:
                st.session_state.v3_dimensiones = ["situación laboral por aclarar"]
                agregar("assistant", "No identifiqué una expresión suficiente. ¿Qué situación concreta del trabajo influye más en cómo te sientes?")
            st.session_state.v3_etapa = "aclaracion"
        else:
            st.session_state.v3_contexto = entrada
            agregar("assistant", "Gracias. Indica ahora con qué frecuencia ocurre.")
            st.session_state.v3_etapa = "frecuencia"
        st.rerun()

elif etapa == "frecuencia":
    valor = st.radio("Frecuencia", ["Ocurrió una vez","Sucede ocasionalmente","Sucede varias veces por semana","Sucede casi todos los días"], index=None)
    if st.button("Continuar", disabled=valor is None):
        st.session_state.v3_frecuencia = valor
        agregar("user", f"Frecuencia: {valor}")
        agregar("assistant", "¿Desde cuándo ocurre?")
        st.session_state.v3_etapa = "duracion"; st.rerun()

elif etapa == "duracion":
    valor = st.radio("Duración", ["Desde hace pocos días","Desde hace varias semanas","Desde hace algunos meses","Desde hace más de seis meses"], index=None)
    if st.button("Continuar", disabled=valor is None):
        st.session_state.v3_duracion = valor
        agregar("user", f"Duración: {valor}")
        agregar("assistant", "Selecciona los aspectos afectados.")
        st.session_state.v3_etapa = "impacto"; st.rerun()

elif etapa == "impacto":
    impactos = st.multiselect("Impactos", ["Descanso","Concentración","Motivación","Relaciones laborales","Vida personal","Cumplimiento de tareas","Ninguno de los anteriores"])
    invalido = "Ninguno de los anteriores" in impactos and len(impactos) > 1
    if invalido: st.error("'Ninguno' debe seleccionarse sin otras opciones.")
    if st.button("Generar orientación", disabled=not impactos or invalido):
        nivel, puntaje = calcular_orientacion(st.session_state.v3_frecuencia, st.session_state.v3_duracion, impactos)
        st.session_state.v3_impactos = impactos; st.session_state.v3_nivel = nivel
        rec = recomendacion_para(st.session_state.v3_dimensiones, nivel, recomendaciones)
        agregar("user", "Impactos: " + ", ".join(impactos))
        agregar("assistant", f"**Orientación experimental: {nivel}**\n\nDimensiones provisionales: {', '.join(st.session_state.v3_dimensiones)}.\n\n{rec}\n\nEsto no constituye diagnóstico ni medición oficial.")
        st.session_state.v3_etapa = "feedback"; st.rerun()

elif etapa == "feedback":
    st.success("Conversación preventiva finalizada")
    comprension = st.radio("¿El sistema comprendió correctamente la situación?", ["Sí","Parcialmente","No"], index=None)
    utilidad = st.slider("Utilidad de la orientación", 1, 5, 3)
    claridad = st.slider("Claridad de la conversación", 1, 5, 3)
    incomoda = st.radio("¿Alguna pregunta resultó incómoda?", ["No","Sí"], index=None)
    if st.button("Enviar evaluación", disabled=comprension is None or incomoda is None):
        registro = {
            "codigo_anonimo": st.session_state.v3_sesion,
            "dimensiones": st.session_state.v3_dimensiones,
            "frecuencia": st.session_state.v3_frecuencia,
            "duracion": st.session_state.v3_duracion,
            "impactos": st.session_state.v3_impactos,
            "orientacion": st.session_state.v3_nivel,
            "comprension": comprension,
            "utilidad": utilidad,
            "claridad": claridad,
            "pregunta_incomoda": incomoda,
            "version_sistema": "3.0",
        }
        ok, msg = guardar_resultado(registro)
        st.info(msg)
        st.session_state.v3_etapa = "fin"

elif etapa == "fin":
    st.success("Gracias por participar en la prueba académica.")
    st.button("Nueva conversación", on_click=reiniciar, type="primary")
