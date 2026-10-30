import streamlit as st
from pydantic import BaseModel, Field
from typing import Literal
from src.ai_budget import can_call, prepare_text, register_usage, MAX_OUTPUT_TOKENS, MODEL_NAME

DIMS=["carga laboral","jornada y desconexión","relaciones y liderazgo","apoyo social y liderazgo","reconocimiento laboral","claridad del rol","autonomía y control","seguridad laboral","relaciones laborales"]
class Analisis(BaseModel):
    relacion:Literal['trabajo','personal','ambas','incierta']
    dimensiones:list[str]=[]
    frecuencia:str|None=None
    duracion:str|None=None
    impactos:list[str]=[]
    pregunta:str=Field(max_length=250)
    resumen:str=Field(max_length=600)
    expresion_nueva:str|None=None

def disponible():
    try:
        return bool(st.secrets.get('GEMINI_API_KEY',''))
    except Exception:
        return False

def analizar(texto,etapa,estado,session_id=None):
    if not disponible(): return None
    permitido,_ = can_call()
    if not permitido: return None
    from google import genai
    entrada=prepare_text(texto)
    prompt=f'''Eres apoyo experimental para un proyecto académico de bienestar laboral. No diagnostiques, no confirmes acoso y no decidas la orientación final. Extrae solo información explícita. Usa dimensiones únicamente de {DIMS}. Formula una sola pregunta cálida. Etapa:{etapa}. Estado:{estado}. Mensaje anonimizado:{entrada}. Devuelve exclusivamente un objeto JSON válido.
    No escribas introducciones como "Here is the JSON requested".
    No uses bloques Markdown.
    No agregues texto antes ni después del objeto JSON.
    Devuelve exclusivamente un objeto JSON válido que cumpla el esquema solicitado.'''
    try:
        cliente=genai.Client(api_key=st.secrets['GEMINI_API_KEY'])
        r = cliente.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": Analisis.model_json_schema(),
                "temperature": 0.2,
                "max_output_tokens": 400,
            },
        )
        if getattr(r, "parsed", None):
            a = r.parsed
        else:
            texto_respuesta = (r.text or "").strip()
            # Retirar bloques Markdown si Gemini los agregó.
            texto_respuesta = texto_respuesta.replace("```json", "")
            texto_respuesta = texto_respuesta.replace("```JSON", "")
            texto_respuesta = texto_respuesta.replace("```", "")
            texto_respuesta = texto_respuesta.strip()

            # Extraer únicamente el objeto JSON.
            inicio_json = texto_respuesta.find("{")
            fin_json = texto_respuesta.rfind("}")

            if inicio_json == -1 or fin_json == -1 or fin_json < inicio_json:
                raise ValueError(
                    "Gemini respondió, pero no devolvió un objeto JSON reconocible. "
                    f"Respuesta recibida: {texto_respuesta[:300]}"
                )

            json_limpio = texto_respuesta[inicio_json:fin_json + 1]
            a = Analisis.model_validate_json(json_limpio)
        a.dimensiones=[d for d in a.dimensiones if d in DIMS][:3]
        register_usage(session_id,etapa,prompt,r.text,True)
        return a
    except Exception as exc:
        print(
        "ERROR_GEMINI:",
        type(exc).__name__,
        str(exc),
        flush=True
        )
        register_usage(session_id,etapa,prompt,str(exc),False)
        return None
