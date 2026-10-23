import uuid, pandas as pd, streamlit as st
from src.core import *
from src.safety import detectar_prioridad, RESPUESTA_PRIORITARIA, RESPUESTA_PELIGRO_INMEDIATO, RESPUESTA_SIN_PELIGRO_INMEDIATO
from src.gemini_v43 import interpretar as interpretar_ia, interpretar_relacion as interpretar_relacion_ia, disponible as ia_disponible
from src.anonymizer import anonimizar
from src.fusion import fusionar
from src.orientation import calcular as calcular_orientacion
from src.proposals import crear as crear_propuesta
from src.storage import guardar as guardar_sesion, disponible as db_disponible
DOG='assets/perrito.png'; HUMAN='assets/persona.png'
st.set_page_config(page_title='Un espacio para escucharte',page_icon='🐾',layout='centered')
st.markdown(r'''<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');:root{--bg:#EEF5F0;--sage:#8EAF98;--p:#527A61;--d:#294B3E;--s:#DDECE1;--w:#FFFDF9;--b:#CFE0D4}html,body,[class*=css]{font-family:Inter,system-ui,sans-serif}.stApp{background:linear-gradient(180deg,#E6F0E8,#F7FAF8 240px)}.block-container{max-width:850px;padding-top:1rem;padding-bottom:7rem}.head{background:linear-gradient(135deg,#527A61,#8EAF98);border-radius:24px;padding:20px 22px;color:white;margin-bottom:12px}.head h1{color:white;margin:0}.head p{margin:4px 0 0}.mascot{width:60px;height:60px;border-radius:50%;border:3px solid #fff;object-fit:cover;animation:float 3s ease-in-out infinite}.row{display:flex;gap:14px;align-items:center}@keyframes float{50%{transform:translateY(-5px)}}[data-testid=stChatMessage]{background:var(--w);border:1px solid var(--b);border-radius:20px;padding:12px 15px;margin:9px 0;box-shadow:0 4px 14px rgba(41,75,62,.05)}[data-testid=stChatMessage]:has([data-testid=chatAvatarIcon-user]){background:var(--s);margin-left:8%}[data-testid=stChatMessage] img{animation:breathe 2.8s ease-in-out infinite}@keyframes breathe{50%{transform:scale(1.06)}}[data-testid=stChatInput]{background:white;border:1px solid var(--sage);border-radius:18px}[data-testid=stChatInput]:focus-within{box-shadow:0 0 0 3px rgba(142,175,152,.2)}[data-testid=stChatInput] button{background:var(--p);color:white}.badge{display:inline-block;background:var(--s);color:var(--p);padding:5px 10px;border-radius:999px;font-size:.78rem}.crisis{background:#FFF7E8;border:1px solid #EBCB8B;border-radius:14px;padding:10px 12px;color:#5E4B22;font-size:.83rem}@media(max-width:640px){.block-container{padding:.7rem .7rem 7rem}[data-testid=stChatMessage]{margin-left:0!important;margin-right:0!important}}</style>''',unsafe_allow_html=True)
import base64
b64=base64.b64encode(open(DOG,'rb').read()).decode()
st.markdown(f'<div class="head"><div class="row"><img class="mascot" src="data:image/png;base64,{b64}"><div><h1>Un espacio para escucharte</h1><p>Conversemos sobre cómo te has sentido y sobre tu experiencia en el trabajo.</p></div></div></div>',unsafe_allow_html=True)
@st.cache_data
def datos():return pd.read_csv('data/diccionario.csv'),pd.read_csv('data/recomendaciones.csv')
def add(r,c):st.session_state.msg.append({'role':r,'content':c})
def init():
 for k,v in {'etapa':'relato','msg':[],'dims':[],'sid':str(uuid.uuid4()),'prioridad_activa':False,'resultado':'sin_clasificar','ia_usada':False,'resumen':None,'propuesta':None}.items():
  if k not in st.session_state:st.session_state[k]=v
 if not st.session_state.msg:add('assistant','¡Hola! Me alegra que estés aquí. 💚\n\nPuedes expresarte con tus propias palabras. Vamos paso a paso.')
def reset():
 for k in list(st.session_state.keys()):st.session_state.pop(k,None)
 st.rerun()
init();df,rec=datos()
with st.expander('Participación y uso de la información', expanded=not st.session_state.get('participa', False)):
 st.checkbox('Acepto participar voluntariamente en esta demostración.', key='participa')
 st.checkbox('Autorizo guardar una copia de esta conversación para revisión académica.', key='autoriza_guardado', disabled=not db_disponible())
 st.checkbox('Autorizo enviar a Gemini fragmentos sin identificadores para interpretar respuestas abiertas.', key='autoriza_ia', disabled=not ia_disponible())
 st.checkbox('Autorizo usar expresiones anonimizadas para proponer mejoras al diccionario.', key='autoriza_aprendizaje', disabled=not db_disponible())
 if not ia_disponible(): st.caption('Gemini no está configurado. Agrega GEMINI_API_KEY en Streamlit Secrets para habilitar esta autorización.')
 if not db_disponible(): st.caption('El guardado no está configurado. Agrega SUPABASE_URL y SUPABASE_KEY para habilitarlo.')
if not st.session_state.get('participa'):st.stop()
a,b=st.columns([5,1])
with a:st.markdown(f'<span class="badge">Etapa: {st.session_state.etapa.replace("_"," ").title()} · IA {"activa" if ia_disponible() and st.session_state.get("autoriza_ia") else "inactiva"}</span>',unsafe_allow_html=True)
with b:st.button('Reiniciar',on_click=reset,use_container_width=True)
for m in st.session_state.msg:
 with st.chat_message(m['role'],avatar=(DOG if m['role']=='assistant' else HUMAN)):st.write(m['content'])
x=st.chat_input('Cuéntame con tus propias palabras...',max_chars=1400)
if x:
 add('user',x)
 # SEGURIDAD SIEMPRE PRIMERO: interrumpe cualquier etapa del flujo.
 if detectar_prioridad(x):
  st.session_state.prioridad_activa=True;st.session_state.etapa='apoyo_prioritario';add('assistant',RESPUESTA_PRIORITARIA);st.rerun()
 if st.session_state.prioridad_activa:
  q=norm(x)
  if q.startswith('si') or q.startswith('sí'):
   add('assistant',RESPUESTA_PELIGRO_INMEDIATO);st.session_state.prioridad_activa=False;st.session_state.etapa='emergencia'
  elif q.startswith('no'):
   add('assistant',RESPUESTA_SIN_PELIGRO_INMEDIATO);st.session_state.prioridad_activa=False;st.session_state.etapa='contexto'
  else:add('assistant','Necesito confirmar algo importante: ¿estás en peligro inmediato en este momento? Responde **sí** o **no**.')
  st.rerun()
 e=st.session_state.etapa
 if e=='relato':st.session_state.dims=detectar(x,df);add('assistant','Gracias por contármelo. ¿Se relaciona principalmente con el trabajo, con una situación personal, con ambas o no estás seguro/a?');st.session_state.etapa='relacion_laboral'
 elif e=='relacion_laboral':
  r=relacion(x)
  fuente_relacion='reglas locales'
  if r is None and ia_disponible() and st.session_state.get('autoriza_ia'):
   r=interpretar_relacion_ia(anonimizar(x))
   fuente_relacion='IA experimental'
  if r=='personal':
   add('assistant','Gracias por contarme cómo te has sentido. 💚\n\nNo hemos identificado elementos suficientes para relacionar tu situación con factores de riesgo psicosocial en el trabajo. Si necesitas apoyo con otros aspectos de tu vida, te animamos a buscar un servicio de orientación adecuado.\n\nTu bienestar es importante. 🌿')
   st.session_state.etapa='fin'
  elif r in ['trabajo','ambas']:
   add('assistant',f'Gracias por aclararlo. ¿Qué situación concreta del trabajo está influyendo? Describe tareas, horarios, trato, cambios o relaciones, sin nombres.\n\n_Interpretación asistida por {fuente_relacion}._')
   st.session_state.etapa='contexto'
  elif r=='incierta':
   add('assistant','Está bien no tenerlo claro todavía. 💚\n\nPodemos explorarlo sin asumir una causa. ¿Qué estaba ocurriendo justo antes de sentirte así y en qué contexto suele suceder?')
   st.session_state.etapa='contexto'
  else:
   add('assistant','No logré interpretar esa respuesta. Puedes decirme si se relaciona con el trabajo, con algo personal, con ambos o si todavía no lo tienes claro.')
 elif e=='contexto':
  mensaje_anonimo=anonimizar(x)
  locales=detectar(mensaje_anonimo,df)
  analisis=None
  if ia_disponible() and st.session_state.get('autoriza_ia'):
   analisis=interpretar_ia(mensaje_anonimo,'contexto',{'dimensiones':st.session_state.dims})
   if analisis:st.session_state.ia_usada=True
  decision=fusionar(locales,analisis)
  st.session_state.dims=list(dict.fromkeys(st.session_state.dims+decision['dimensiones']))
  if analisis and st.session_state.get('autoriza_aprendizaje'):st.session_state.propuesta=crear_propuesta(analisis,mensaje_anonimo)
  if decision['dimensiones']:
   add('assistant',f"Podría haber elementos relacionados con {', '.join(st.session_state.dims)}. ¿Representa lo que quisiste expresar? Responde sí, parcialmente o no.\n\n_Interpretación asistida por {decision['fuente']}._")
   st.session_state.etapa='confirmar'
  else:add('assistant',decision['pregunta'])
 elif e=='confirmar':
  q=norm(x)
  if q.startswith('no') or 'parcial' in q:add('assistant','Gracias por corregirme. ¿Cómo describirías el aspecto laboral principal?');st.session_state.etapa='contexto'
  elif 'si' in q:add('assistant','¿Con qué frecuencia ocurre?');st.session_state.etapa='frecuencia'
  else:add('assistant','¿La interpretación fue correcta? Responde sí, parcialmente o no.')
 elif e=='frecuencia':
  analisis=interpretar_ia(anonimizar(x),'frecuencia',{'dimensiones':st.session_state.dims}) if ia_disponible() and st.session_state.get('autoriza_ia') else None
  v=analisis.frecuencia if analisis and analisis.frecuencia else frecuencia(x)
  if v:st.session_state.frec=v;add('assistant',analisis.pregunta_siguiente if analisis and analisis.pregunta_siguiente else '¿Desde cuándo ocurre?');st.session_state.etapa='duracion'
  else:add('assistant','No entendí la frecuencia. ¿Ocurrió una vez, a veces, varias veces por semana o casi todos los días?')
 elif e=='duracion':
  analisis=interpretar_ia(anonimizar(x),'duracion',{'frecuencia':st.session_state.get('frec')}) if ia_disponible() and st.session_state.get('autoriza_ia') else None
  v=analisis.duracion if analisis and analisis.duracion else duracion(x)
  if v:st.session_state.dur=v;add('assistant',analisis.pregunta_siguiente if analisis and analisis.pregunta_siguiente else '¿Cómo te ha afectado esta situación?');st.session_state.etapa='impacto'
  else:add('assistant','No entendí la duración. ¿Desde hace días, semanas, meses o más de seis meses?')
 elif e=='impacto':
  analisis=interpretar_ia(anonimizar(x),'impactos',{'frecuencia':st.session_state.get('frec'),'duracion':st.session_state.get('dur')}) if ia_disponible() and st.session_state.get('autoriza_ia') else None
  v=list(analisis.impactos) if analisis and analisis.impactos else impactos(x)
  if v:
   st.session_state.imps=v
   if analisis and analisis.resumen_neutral:
    st.session_state.resumen=analisis.resumen_neutral;add('assistant',f"Antes de continuar, este es un resumen neutral de lo conversado:\n\n**{st.session_state.resumen}**\n\n¿Representa correctamente lo que compartiste?");st.session_state.etapa='confirmar_resumen'
   else:
    r=calcular_orientacion(st.session_state.frec,st.session_state.dur,v);st.session_state.resultado=r['orientacion'];add('assistant',f"**Resultado preventivo provisional: {r['orientacion']}**\n\nCalculado mediante reglas locales ({r['version']}). Gemini no decide la orientación final.");st.session_state.etapa='fin'
  else:add('assistant','¿Ha afectado descanso, concentración, motivación, relaciones, vida personal o tareas?')
 elif e=='confirmar_resumen':
  if norm(x).startswith('si'):
   r=calcular_orientacion(st.session_state.frec,st.session_state.dur,st.session_state.imps);st.session_state.resultado=r['orientacion'];add('assistant',f"**Resultado preventivo provisional: {r['orientacion']}**\n\nCalculado mediante reglas locales ({r['version']}). Gemini no decide la orientación final.");st.session_state.etapa='fin'
  else:add('assistant','Gracias por corregirlo. Cuéntame qué parte debería ajustar.');st.session_state.etapa='contexto'
 elif e in ['fin','emergencia','apoyo_humano']:
  if st.session_state.get('autoriza_guardado') and db_disponible():
   guardar_sesion({'codigo_anonimo':st.session_state.sid,'mensajes':st.session_state.msg,'dimensiones':st.session_state.dims,'orientacion':st.session_state.resultado,'version':'4.3'})
  add('assistant','La conversación terminó. Usa Reiniciar para comenzar otra prueba.')
 st.rerun()
