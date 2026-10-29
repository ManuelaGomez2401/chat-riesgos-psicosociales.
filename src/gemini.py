import json,streamlit as st
from pydantic import BaseModel,Field
from typing import Literal
DIMS=["carga laboral","jornada y desconexión","relaciones y liderazgo","apoyo social y liderazgo","reconocimiento laboral","claridad del rol","autonomía y control","seguridad laboral","relaciones laborales"]
class Analisis(BaseModel):
 relacion:Literal['trabajo','personal','ambas','incierta']
 dimensiones:list[str]=[]
 frecuencia:str|None=None;duracion:str|None=None;impactos:list[str]=[]
 pregunta:str=Field(max_length=250);resumen:str=Field(max_length=600);expresion_nueva:str|None=None

def disponible():
 try:return bool(st.secrets.get('GEMINI_API_KEY',''))
 except:return False
def analizar(texto,etapa,estado):
 if not disponible():return None
 from google import genai
 cliente=genai.Client(api_key=st.secrets['GEMINI_API_KEY'])
 prompt=f'''Eres apoyo experimental para un proyecto académico de bienestar laboral. No diagnostiques, no confirmes acoso y no decidas la orientación final. Extrae solo información explícita. Usa dimensiones únicamente de {DIMS}. Formula una sola pregunta cálida. Etapa:{etapa}. Estado:{estado}. Mensaje anonimizado:{texto}'''
 try:
  r=cliente.models.generate_content(model='gemini-2.5-flash',contents=prompt,config={'response_mime_type':'application/json','response_schema':Analisis,'temperature':0.2})
  a=r.parsed if getattr(r,'parsed',None) else Analisis.model_validate_json(r.text);a.dimensiones=[d for d in a.dimensiones if d in DIMS][:3];return a
 except Exception:return None
