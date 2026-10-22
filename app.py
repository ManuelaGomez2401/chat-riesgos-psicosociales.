import uuid,pandas as pd,streamlit as st
from src.core import *
st.set_page_config(page_title='Un espacio para escucharte',page_icon='🌿',layout='centered')
st.markdown(r'''<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');:root{--bg:#F7FAF8;--sage:#8EAF98;--p:#527A61;--d:#294B3E;--s:#EAF3EC;--w:#FFF;--b:#DCE8E0;--m:#73867C}html,body,[class*=css]{font-family:Inter,system-ui,sans-serif}.stApp{background:var(--bg);color:var(--d)}.block-container{max-width:820px;padding-top:1rem;padding-bottom:7rem}.head{background:var(--w);border:1px solid var(--b);border-radius:22px;padding:18px 20px;margin-bottom:10px}.row{display:flex;gap:13px;align-items:center}.ico{width:44px;height:44px;border-radius:14px;background:var(--s);display:flex;align-items:center;justify-content:center;font-size:23px}.head h1{color:var(--d);font-size:1.5rem;margin:0}.sub{color:var(--p);margin:3px 0}.reas{color:var(--m);font-size:.86rem;line-height:1.45;margin:10px 0 0}.privacy{color:var(--m);background:#F1F6F2;border:1px solid var(--b);padding:9px 12px;border-radius:12px;font-size:.81rem;margin-bottom:10px}[data-testid=stChatMessage]{background:var(--w);border:1px solid var(--b);border-radius:18px;padding:12px 15px;margin:8px 0;box-shadow:none}[data-testid=stChatMessage] p{color:var(--d);font-size:.98rem;line-height:1.58}[data-testid=stChatMessage]:has([data-testid=chatAvatarIcon-user]){background:var(--s);border-color:#CFE0D4;margin-left:7%}[data-testid=stChatMessage]:has([data-testid=chatAvatarIcon-assistant]){margin-right:7%}[data-testid=stChatInput]{background:var(--w);border:1px solid var(--b);border-radius:18px;box-shadow:0 6px 18px rgba(41,75,62,.08)}[data-testid=stChatInput]:focus-within{border-color:var(--sage);box-shadow:0 0 0 3px rgba(142,175,152,.18)}[data-testid=stChatInput] button{background:var(--p);color:white;border-radius:12px}.stButton>button{border:1px solid var(--b);color:var(--p);background:var(--w);border-radius:12px}.stage{display:inline-block;background:var(--s);color:var(--p);padding:5px 10px;border-radius:999px;font-size:.78rem;font-weight:600}@media(max-width:640px){.block-container{padding:.7rem .7rem 7rem}.head{padding:15px}.head h1{font-size:1.25rem}[data-testid=stChatMessage]{margin-left:0!important;margin-right:0!important}}</style><div class="head"><div class="row"><div class="ico">🌿</div><div><h1>Un espacio para escucharte</h1><p class="sub">Conversemos sobre cómo te has sentido y sobre tu experiencia en el trabajo.</p></div></div><p class="reas">Puedes expresarte con tranquilidad y con tus propias palabras. No necesitas responder de una manera determinada. Vamos paso a paso.</p></div><div class="privacy">Evita incluir información que permita identificar a una persona o empresa real.</div>''',unsafe_allow_html=True)
@st.cache_data
def datos():return pd.read_csv('data/diccionario.csv'),pd.read_csv('data/recomendaciones.csv')
def add(r,c):st.session_state.msg.append({'role':r,'content':c})
def init():
 for k,v in {'etapa':'relato','msg':[],'dims':[],'intentos':0,'sid':str(uuid.uuid4())}.items():
  if k not in st.session_state:st.session_state[k]=v
 if not st.session_state.msg:add('assistant','¡Hola! Me alegra que estés aquí. 💚\n\nEste es un espacio para conversar sobre cómo te has sentido últimamente y sobre las situaciones que has vivido en tu entorno laboral.\n\nPuedes expresarte con tus propias palabras. No necesitas encontrar las palabras perfectas ni responder de una manera determinada.\n\nVamos paso a paso.')
def reset():
 for k in ['etapa','msg','dims','intentos','sid','frec','dur','imps']:st.session_state.pop(k,None)
 st.rerun()
if not st.checkbox('Comprendo que este es un prototipo académico y acepto participar voluntariamente.'):st.stop()
init();df,rec=datos();a,b=st.columns([5,1])
with a:st.markdown(f'<span class="stage">Etapa: {st.session_state.etapa.replace("_"," ").title()}</span>',unsafe_allow_html=True)
with b:st.button('Reiniciar',on_click=reset,use_container_width=True)
for m in st.session_state.msg:
 with st.chat_message(m['role']):st.write(m['content'])
x=st.chat_input('Cuéntame con tus propias palabras...',max_chars=1400)
if x:
 add('user',x);e=st.session_state.etapa
 if e=='relato':st.session_state.dims=detectar(x,df);add('assistant','Gracias por contármelo. ¿Consideras que esto se debe principalmente al trabajo, a una situación personal, a ambas cosas o no estás seguro/a?');st.session_state.etapa='relacion laboral'
 elif e=='relacion laboral':
  r=relacion(x)
  if r=='personal':add('assistant','Gracias por contarme cómo te has sentido. 💚\n\nPor lo que hemos conversado, no hemos identificado elementos suficientes para relacionar tu situación con factores de riesgo psicosocial en el trabajo.\n\nEste espacio está enfocado en explorar experiencias y situaciones del entorno laboral. Si lo que necesitas está relacionado con otros aspectos de tu vida, te animamos a buscar un servicio de orientación o apoyo que pueda acompañarte de acuerdo con tu situación.\n\nTu bienestar es importante. Gracias por compartir este momento conmigo. 🌿');st.session_state.etapa='fin'
  elif r in ['trabajo','ambas','incierta']:add('assistant','¿Qué situación concreta del trabajo está influyendo? Describe tareas, horarios, trato, cambios o relaciones, sin nombres.');st.session_state.etapa='contexto'
  else:add('assistant','¿Dirías que se relaciona con el trabajo, con algo personal, con ambos o aún no lo tienes claro?')
 elif e=='contexto':
  d=detectar(x,df);st.session_state.dims=list(dict.fromkeys(st.session_state.dims+d))
  if d:add('assistant',f"Podría haber elementos relacionados con {', '.join(st.session_state.dims)}. ¿Representa lo que quisiste expresar? Responde sí, parcialmente o no.");st.session_state.etapa='confirmar';st.session_state.intentos=0
  else:
   st.session_state.intentos+=1
   if st.session_state.intentos==1:add('assistant','¿Se relaciona principalmente con carga de trabajo, horarios o descanso, trato recibido, apoyo, funciones, autonomía, reconocimiento o estabilidad laboral?')
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
   n=nivel(st.session_state.frec,st.session_state.dur,v);dims=st.session_state.dims or ['situación por aclarar'];m=rec[(rec.dimension.isin(dims))&(rec.nivel==n)];m=m if not m.empty else rec[(rec.dimension=='general')&(rec.nivel==n)];txt=m.iloc[0].mensaje if not m.empty else 'Observa la evolución.';add('assistant',f'**Resultado preventivo provisional: {n}.**\n\nAspectos explorados: {", ".join(dims)}.\n\n{txt}\n\nNo es diagnóstico ni medición oficial. ¿Representa lo conversado?');st.session_state.etapa='feedback'
  else:add('assistant','¿Ha afectado descanso, concentración, motivación, relaciones, vida personal o tareas?')
 elif e=='feedback':add('assistant','Gracias por tu retroalimentación y por compartir este momento. 🌿');st.session_state.etapa='fin'
 elif e=='fin':add('assistant','La conversación terminó. Usa Reiniciar para comenzar otra prueba.')
 st.rerun()
