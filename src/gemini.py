import streamlit as st
from src.schemas import InterpretacionIA,CierreIA
BASE="""Eres el apoyo conversacional de un prototipo universitario sobre bienestar laboral. Usa un tono cálido, natural y respetuoso. No diagnostiques, no confirmes acoso, no des consejo médico, no afirmes que un riesgo existe o no existe de forma absoluta y no decidas la orientación final. Haz una sola pregunta cuando corresponda."""
def disponible():
 try:return bool(st.secrets.get('GEMINI_API_KEY',''))
 except:return False
def _cliente():
 from google import genai
 return genai.Client(api_key=st.secrets['GEMINI_API_KEY'])
def interpretar(texto,etapa,estado):
 if not disponible():return None
 try:
  r=_cliente().models.generate_content(model='gemini-2.5-flash',contents=f"{BASE}\nEtapa:{etapa}\nEstado confirmado:{estado}\nMensaje anonimizado:{texto}",config={'response_mime_type':'application/json','response_schema':InterpretacionIA,'temperature':0.25})
  return r.parsed if getattr(r,'parsed',None) else InterpretacionIA.model_validate_json(r.text)
 except Exception:return None
def redactar_cierre(tipo,datos):
 if not disponible():return None
 instrucciones={
 'acompanamiento':'Redacta un mensaje de 110 a 170 palabras. Agradece, explica que por frecuencia, duración e impactos podría ser útil hablar con una persona capacitada. Aclara que no es diagnóstico ni confirmación. Menciona bienestar, SST o apoyo psicológico. Termina preguntando si representa lo que necesita.',
 'sin_indicadores':'Redacta un mensaje de 90 a 150 palabras. Expresa alegría prudente porque con lo compartido no se identificaron señales suficientes de afectación laboral. No garantices ausencia de riesgo. Invita a volver al chat y a cuidar el bienestar.',
 'informacion_insuficiente':'Redacta un mensaje de 80 a 130 palabras. Agradece lo compartido, explica que no hay información suficiente para concluir y deja abierta la posibilidad de regresar.'}
 try:
  r=_cliente().models.generate_content(model='gemini-2.5-flash',contents=f"{BASE}\n{instrucciones[tipo]}\nDatos:{datos}",config={'response_mime_type':'application/json','response_schema':CierreIA,'temperature':0.35})
  obj=r.parsed if getattr(r,'parsed',None) else CierreIA.model_validate_json(r.text);return obj.mensaje
 except Exception:return None
