import streamlit as st
from src.schemas import InterpretacionIA

PROMPT="""Eres un componente experimental para comprender lenguaje en un proyecto universitario sobre experiencias laborales. No diagnostiques, no confirmes acoso, no des consejo médico y no decidas la orientación final. Extrae solo información respaldada por el mensaje. Formula una sola pregunta cálida, neutral y breve."""

def disponible():
    try:return bool(st.secrets.get("GEMINI_API_KEY",""))
    except Exception:return False

def interpretar(texto_anonimo,etapa,contexto):
    if not disponible():return None
    from google import genai
    cliente=genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    contenido=f"{PROMPT}\nEtapa: {etapa}\nContexto confirmado: {contexto}\nMensaje: {texto_anonimo}"
    try:
        respuesta=cliente.models.generate_content(model="gemini-2.5-flash",contents=contenido,config={"response_mime_type":"application/json","response_schema":InterpretacionIA,"temperature":0.2})
        if getattr(respuesta,"parsed",None):return respuesta.parsed
        return InterpretacionIA.model_validate_json(respuesta.text)
    except Exception:return None
