import uuid, pandas as pd, streamlit as st
from src.core import *
from src.safety import detectar_prioridad, RESPUESTA_PRIORITARIA, RESPUESTA_PELIGRO_INMEDIATO, RESPUESTA_SIN_PELIGRO_INMEDIATO
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
 for k,v in {'etapa':'relato','msg':[],'dims':[],'sid':str(uuid.uuid4()),'prioridad_activa':False}.items():
  if k not in st.session_state:st.session_state[k]=v
 if not st.session_state.msg:add('assistant','¡Hola! Me alegra que estés aquí. 💚\n\nPuedes expresarte con tus propias palabras. Vamos paso a paso.')
def reset():
 for k in list(st.session_state.keys()):st.session_state.pop(k,None)
 st.rerun()
init();df,rec=datos()
if not st.checkbox('Acepto participar voluntariamente en esta demostración.',key='participa'):st.stop()
a,b=st.columns([5,1])
with a:st.markdown(f'<span class="badge">Etapa: {st.session_state.etapa.replace("_"," ").title()}</span>',unsafe_allow_html=True)
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
   add('assistant',RESPUESTA_PELIGRO_INMEDIATO);st.session_state.etapa='emergencia'
  elif q.startswith('no'):
   add('assistant',RESPUESTA_SIN_PELIGRO_INMEDIATO);st.session_state.etapa='apoyo_humano'
  else:add('assistant','Necesito confirmar algo importante: ¿estás en peligro inmediato en este momento? Responde **sí** o **no**.')
  st.rerun()
 e=st.session_state.etapa
 if e=='relato':st.session_state.dims=detectar(x,df);add('assistant','Gracias por contármelo. ¿Se relaciona principalmente con el trabajo, con una situación personal, con ambas o no estás seguro/a?');st.session_state.etapa='relacion_laboral'
 elif e=='relacion_laboral':
  r=relacion(x)
  if r=='personal':add('assistant','Gracias por contarme cómo te has sentido. 💚\n\nNo hemos identificado elementos suficientes para relacionar tu situación con factores de riesgo psicosocial en el trabajo. Si lo que necesitas está relacionado con otros aspectos de tu vida, te animamos a buscar un servicio de orientación o apoyo adecuado.\n\nTu bienestar es importante. Gracias por compartir este momento conmigo. 🌿');st.session_state.etapa='fin'
  elif r in ['trabajo','ambas','incierta']:add('assistant','¿Qué situación concreta del trabajo está influyendo? Describe tareas, horarios, trato, cambios o relaciones, sin nombres.');st.session_state.etapa='contexto'
  else:add('assistant','¿Dirías que se relaciona con el trabajo, con algo personal, con ambos o aún no lo tienes claro?')
 elif e=='contexto':
  d=detectar(x,df);st.session_state.dims=list(dict.fromkeys(st.session_state.dims+d))
  if d:add('assistant',f"Podría haber elementos relacionados con {', '.join(st.session_state.dims)}. ¿Representa lo que quisiste expresar? Responde sí, parcialmente o no.");st.session_state.etapa='confirmar'
  else:add('assistant','¿Se relaciona con carga de trabajo, horarios, trato, apoyo, funciones, autonomía, reconocimiento o estabilidad laboral?')
 elif e=='confirmar':
  q=norm(x)
  if q.startswith('no') or 'parcial' in q:add('assistant','Gracias por corregirme. ¿Cómo describirías el aspecto laboral principal?');st.session_state.etapa='contexto'
  elif 'si' in q:add('assistant','¿Con qué frecuencia ocurre?');st.session_state.etapa='frecuencia'
  else:add('assistant','¿La interpretación fue correcta? Responde sí, parcialmente o no.')
 elif e=='frecuencia':
  v=frecuencia(x)
  if v:st.session_state.frec=v;add('assistant','¿Desde cuándo ocurre?');st.session_state.etapa='duracion'
  else:add('assistant','No entendí la frecuencia. ¿Ocurrió una vez, a veces, varias veces por semana o casi todos los días?')
 elif e=='duracion':
  v=duracion(x)
  if v:st.session_state.dur=v;add('assistant','¿Cómo te ha afectado? Puedes mencionar sueño, concentración, motivación, relaciones, vida personal o tareas.');st.session_state.etapa='impacto'
  else:add('assistant','No entendí la duración. ¿Desde hace días, semanas, meses o más de seis meses?')
 elif e=='impacto':
  v=impactos(x)
  if v:
   n=nivel(st.session_state.frec,st.session_state.dur,v);dims=st.session_state.dims or ['situación por aclarar'];m=rec[(rec.dimension.isin(dims))&(rec.nivel==n)];m=m if not m.empty else rec[(rec.dimension=='general')&(rec.nivel==n)];txt=m.iloc[0].mensaje if not m.empty else 'Observa la evolución.';add('assistant',f'**Resultado preventivo provisional: {n}.**\n\nAspectos explorados: {", ".join(dims)}.\n\n{txt}\n\nNo es diagnóstico ni medición oficial.');st.session_state.etapa='fin'
  else:add('assistant','¿Ha afectado descanso, concentración, motivación, relaciones, vida personal o tareas?')
 elif e in ['fin','emergencia','apoyo_humano']:add('assistant','La conversación terminó. Usa Reiniciar para comenzar otra prueba.')
 st.rerun()
