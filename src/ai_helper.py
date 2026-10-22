import json
import streamlit as st
DIMENSIONES=['carga laboral','jornada y desconexión','relaciones y liderazgo','apoyo social y liderazgo','reconocimiento laboral','claridad del rol','autonomía y control','seguridad laboral','relaciones laborales']
def disponible():
 try:return bool(st.secrets.get('GEMINI_API_KEY',''))
 except:return False
def interpretar(texto):
 if not disponible():return None
 from google import genai
 client=genai.Client(api_key=st.secrets['GEMINI_API_KEY'])
 prompt=f'''Analiza un mensaje de un prototipo académico sobre experiencias laborales. No diagnostiques, no confirmes acoso, no des consejo médico y no asumas que el trabajo es la causa. Devuelve SOLO JSON válido: {{"relacion_laboral":"clara|posible|no_clara","dimensiones":[],"pregunta_aclaratoria":"","resumen_neutral":""}}. Las dimensiones permitidas son: {DIMENSIONES}. Mensaje anonimizado: {texto[:1200]}'''
 try:
  r=client.models.generate_content(model='gemini-2.5-flash',contents=prompt)
  raw=r.text.strip().replace('```json','').replace('```','').strip();data=json.loads(raw)
  data['dimensiones']=[d for d in data.get('dimensiones',[]) if d in DIMENSIONES][:3]
  return data
 except Exception:return None
