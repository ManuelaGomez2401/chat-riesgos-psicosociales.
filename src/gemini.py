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
    prompt=f'''Eres apoyo experimental para un proyecto académico de bienestar laboral. No diagnostiques, no confirmes acoso y no decidas la orientación final. Extrae solo información explícita. Usa dimensiones únicamente de {DIMS}. Formula una sola pregunta cálida. Etapa:{etapa}. Estado:{estado}. Mensaje anonimizado:{entrada}'''
    try:
        cliente=genai.Client(api_key=st.secrets['GEMINI_API_KEY'])
        r=cliente.models.generate_content(model=MODEL_NAME,contents=prompt,config={'response_mime_type':'application/json','response_schema':Analisis,'temperature':0.2,'max_output_tokens':MAX_OUTPUT_TOKENS})
        a=r.parsed if getattr(r,'parsed',None) else Analisis.model_validate_json(r.text)
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
