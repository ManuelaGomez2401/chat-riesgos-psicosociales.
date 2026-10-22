import uuid,pandas as pd,streamlit as st
from src.core import *
from src.ai_helper import interpretar as ia_interpretar,disponible as ia_disponible
from src.storage import guardar_sesion,disponible as db_disponible
DOG='assets/perrito_asistente.png'
st.set_page_config(page_title='Un espacio para escucharte',page_icon='🐾',layout='centered')
st.markdown(r'''<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');:root{--bg:#EEF5F0;--sage:#8EAF98;--p:#527A61;--d:#294B3E;--s:#DDECE1;--w:#FFFDF9;--b:#CFE0D4;--m:#6D8175}html,body,[class*=css]{font-family:Inter,system-ui,sans-serif}.stApp{background:linear-gradient(180deg,#E6F0E8 0,#F7FAF8 240px);color:var(--d)}.block-container{max-width:850px;padding-top:1rem;padding-bottom:7rem}.head{background:linear-gradient(135deg,#527A61,#8EAF98);border-radius:24px;padding:20px 22px;margin-bottom:12px;color:white}.headrow{display:flex;gap:15px;align-items:center}.mascot{width:62px;height:62px;border-radius:50%;border:3px solid rgba(255,255,255,.75);object-fit:cover;animation:floatDog 3s ease-in-out infinite}.head h1{color:white;font-size:1.55rem;margin:0}.head p{margin:4px 0 0;color:#F4FAF6}.reassure{font-size:.86rem;opacity:.95;margin-top:10px!important}@keyframes floatDog{0%,100%{transform:translateY(0) rotate(-1deg)}50%{transform:translateY(-5px) rotate(1deg)}}[data-testid=stChatMessage]{background:var(--w);border:1px solid var(--b);border-radius:20px;padding:12px 15px;margin:9px 0;box-shadow:0 4px 14px rgba(41,75,62,.05)}[data-testid=stChatMessage]:has([data-testid=chatAvatarIcon-user]){background:var(--s);margin-left:8%}[data-testid=stChatMessage] img{animation:avatarBreath 2.8s ease-in-out infinite}@keyframes avatarBreath{0%,100%{transform:scale(1)}50%{transform:scale(1.07)}}[data-testid=stChatMessage] p{color:var(--d);line-height:1.58}[data-testid=stChatInput]{background:#fff;border:1px solid var(--sage);border-radius:18px;box-shadow:0 6px 18px rgba(41,75,62,.09)}[data-testid=stChatInput]:focus-within{box-shadow:0 0 0 3px rgba(142,175,152,.22)}[data-testid=stChatInput] button{background:var(--p);color:white;border-radius:12px}.privacy{background:#F7FAF8;border:1px solid var(--b);color:var(--m);padding:9px 12px;border-radius:12px;font-size:.81rem}.badge{display:inline-block;background:#DDECE1;color:#41664E;padding:5px 10px;border-radius:999px;font-size:.76rem;font-weight:600}.stButton>button{border-color:var(--sage);color:var(--p);border-radius:12px}@media(max-width:640px){.block-container{padding:.7rem .7rem 7rem}.head{padding:16px}.mascot{width:52px;height:52px}.head h1{font-size:1.25rem}[data-testid=stChatMessage]{margin-left:0!important;margin-right:0!important}}</style>''',unsafe_allow_html=True)
import base64
b64=base64.b64encode(open(DOG,'rb').read()).decode()
st.markdown(f'''<div class="head"><div class="headrow"><img class="mascot" src="data:image/png;base64,{b64}"><div><h1>Un espacio para escucharte</h1><p>Conversemos sobre cómo te has sentido y sobre tu experiencia en el trabajo.</p></div></div><p class="reassure">Puedes expresarte con tranquilidad. No necesitas encontrar las palabras perfectas. Vamos paso a paso.</p></div><div class="privacy">Evita incluir información que permita identificar a una persona o empresa real. La IA, si está activa, se usa solo como apoyo experimental.</div>''',unsafe_allow_html=True)
@st.cache_data
def datos():return pd.read_csv('data/diccionario.csv'),pd.read_csv('data/recomendaciones.csv')
def add(r,c):st.session_state.msg.append({'role':r,'content':c})
def init():
 for k,v in {'etapa':'relato','msg':[],'dims':[],'intentos':0,'sid':str(uuid.uuid4()),'consent_save':False,'consent_ai':False}.items():
  if k not in st.session_state:st.session_state[k]=v
 if not st.session_state.msg:add('assistant','¡Hola! Me alegra que estés aquí. 💚\n\nEste es un espacio para conversar sobre cómo te has sentido últimamente y sobre las situaciones que has vivido en tu entorno laboral.\n\nPuedes expresarte con tus propias palabras. Vamos paso a paso.')
def reset():
 for k in list(st.session_state.keys()):
  if k not in ['consent_save','consent_ai']:st.session_state.pop(k,None)
 st.rerun()
init();df,rec=datos()
with st.expander('Participación y uso de la información',expanded=not st.session_state.msg):
 st.checkbox('Acepto participar voluntariamente en esta demostración.',key='participa')
 st.checkbox('Autorizo guardar una copia de esta conversación para revisión académica.',key='consent_save')
 st.checkbox('Autorizo enviar fragmentos sin identificadores a Gemini cuando el detector no comprenda.',key='consent_ai',disabled=not ia_disponible())
if not st.session_state.get('participa'):st.stop()
a,b=st.columns([5,1])
with a:st.markdown(f'<span class="badge">Etapa: {st.session_state.etapa.replace("_"," ").title()} · IA {"activa" if ia_disponible() and st.session_state.consent_ai else "inactiva"}</span>',unsafe_allow_html=True)
with b:st.button('Reiniciar',on_click=reset,use_container_width=True)
for m in st.session_state.msg:
 with st.chat_message(m['role'],avatar=(DOG if m['role']=='assistant' else '🙂')):st.write(m['content'])
x=st.chat_input('Cuéntame con tus propias palabras...',max_chars=1400)
if x:
 add('user',x);e=st.session_state.etapa
 if e=='relato':st.session_state.relato=x;st.session_state.dims=[h['dimension'] for h in detectar(x,df)];add('assistant','Gracias por contármelo. ¿Consideras que esto se debe principalmente al trabajo, a una situación personal, a ambas cosas o no estás seguro/a?');st.session_state.etapa='relacion_laboral'
 elif e=='relacion_laboral':
  r=relacion(x)
  if r=='personal':add('assistant','Gracias por contarme cómo te has sentido. 💚\n\nPor lo que hemos conversado, no hemos identificado elementos suficientes para relacionar tu situación con factores de riesgo psicosocial en el trabajo.\n\nEste espacio está enfocado en explorar experiencias y situaciones del entorno laboral. Si lo que necesitas está relacionado con otros aspectos de tu vida, te animamos a buscar un servicio de orientación o apoyo que pueda acompañarte de acuerdo con tu situación.\n\nTu bienestar es importante. Gracias por compartir este momento conmigo. 🌿');st.session_state.etapa='fin'
  elif r in ['trabajo','ambas','incierta']:add('assistant','¿Qué situación concreta del trabajo está influyendo? Describe tareas, horarios, trato, cambios o relaciones, sin nombres.');st.session_state.etapa='contexto'
  else:add('assistant','¿Dirías que se relaciona con el trabajo, con algo personal, con ambos o aún no lo tienes claro?')
 elif e=='contexto':
  ds=[h['dimension'] for h in detectar(x,df)]
  if not ds and ia_disponible() and st.session_state.consent_ai:
   ai=ia_interpretar(x)
   if ai:ds=ai.get('dimensiones',[]);st.session_state.ai_question=ai.get('pregunta_aclaratoria','')
  st.session_state.dims=list(dict.fromkeys(st.session_state.dims+ds))
  if ds:add('assistant',f"Podría haber elementos relacionados con {', '.join(st.session_state.dims)}. ¿Representa lo que quisiste expresar? Responde sí, parcialmente o no.");st.session_state.etapa='confirmar';st.session_state.intentos=0
  else:
   st.session_state.intentos+=1
   if st.session_state.intentos==1:add('assistant','¿Se relaciona con carga de trabajo, horarios, trato, apoyo, funciones, autonomía, reconocimiento o estabilidad laboral?')
   elif st.session_state.intentos==2:add('assistant','Todavía no tengo información suficiente. Puedes contar un ejemplo concreto o escribir “finalizar”.')
   else:add('assistant','No fue posible identificar una condición laboral con suficiente claridad. Cerraremos sin clasificar para evitar una conclusión incorrecta.');st.session_state.etapa='fin'
 elif e=='confirmar':
  q=norm(x)
  if q.startswith('no') or 'parcial' in q:add('assistant','Gracias por corregirme. ¿Cómo describirías el aspecto laboral principal?');st.session_state.etapa='contexto'
  elif 'si' in q:add('assistant','¿Con qué frecuencia ocurre? Puedes escribir “dos veces por semana” o “casi todos los días”.');st.session_state.etapa='frecuencia'
  else:add('assistant','¿La interpretación fue correcta? Responde sí, parcialmente o no.')
 elif e=='frecuencia':
  v=frecuencia(x)
  if v:st.session_state.frec=v;add('assistant','¿Desde cuándo ocurre? Por ejemplo: “hace tres semanas” o “desde hace dos meses”.');st.session_state.etapa='duracion'
  else:add('assistant','No entendí la frecuencia. ¿Ocurrió una vez, a veces, varias veces por semana o casi todos los días?')
 elif e=='duracion':
  v=duracion(x)
  if v:st.session_state.dur=v;add('assistant','¿Cómo te ha afectado? Puedes mencionar sueño, concentración, motivación, relaciones, vida personal o tareas.');st.session_state.etapa='impacto'
  else:add('assistant','No entendí la duración. ¿Desde hace días, semanas, meses o más de seis meses?')
 elif e=='impacto':
  v=impactos(x)
  if v:
   st.session_state.imps=v;n=nivel(st.session_state.frec,st.session_state.dur,v);st.session_state.resultado=n;dims=st.session_state.dims or ['situación por aclarar'];m=rec[(rec.dimension.isin(dims))&(rec.nivel==n)];m=m if not m.empty else rec[(rec.dimension=='general')&(rec.nivel==n)];txt=m.iloc[0].mensaje if not m.empty else 'Observa la evolución.';add('assistant',f'**Resultado preventivo provisional: {n}.**\n\nAspectos explorados: {", ".join(dims)}.\n\n{txt}\n\nNo es diagnóstico ni medición oficial. ¿Representa lo conversado?');st.session_state.etapa='feedback'
  else:add('assistant','¿Ha afectado descanso, concentración, motivación, relaciones, vida personal o tareas?')
 elif e=='feedback':
  if st.session_state.consent_save:
   guardar_sesion({'codigo_anonimo':st.session_state.sid,'mensajes':st.session_state.msg,'dimensiones':st.session_state.dims,'orientacion':st.session_state.get('resultado','sin_clasificar'),'retroalimentacion':x,'version':'4.0'})
  add('assistant','Gracias por tu retroalimentación y por compartir este momento. 🌿');st.session_state.etapa='fin'
 elif e=='fin':add('assistant','La conversación terminó. Usa Reiniciar para comenzar otra prueba.')
 st.rerun()
