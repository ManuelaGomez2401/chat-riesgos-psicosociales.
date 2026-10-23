import base64,uuid,pandas as pd,streamlit as st
from src.anonymizer import anonimizar
from src.gemini import disponible as ia_disponible,interpretar,redactar_cierre
from src.local import norm,relacion,detectar,frecuencia,duracion,impactos
from src.messages import BIENVENIDA,ACOMPANAMIENTO,SIN_INDICADORES,INSUFICIENTE
from src.orientation import calcular
from src.safety import detectar_prioridad,PRIORIDAD,PELIGRO,NO_PELIGRO
DOG='assets/perrito.png';HUMAN='assets/persona.png'
st.set_page_config(page_title='Un espacio para escucharte',page_icon='🐾',layout='centered')
st.markdown(r'''<style>:root{--p:#527A61;--s:#DDECE1;--b:#CFE0D4;--w:#FFFDF9}.stApp{background:linear-gradient(180deg,#DDECE1,#F7FAF8 250px)}.block-container{max-width:860px;padding-top:1rem;padding-bottom:7rem}.head{background:linear-gradient(135deg,#476B55,#8EAF98);border-radius:24px;padding:20px;color:white}.head h1{color:white;margin:0}.row{display:flex;gap:14px;align-items:center}.mascot{width:62px;height:62px;border-radius:50%;border:3px solid white;animation:f 3s ease-in-out infinite}@keyframes f{50%{transform:translateY(-5px)}}[data-testid=stChatMessage]{background:var(--w);border:1px solid var(--b);border-radius:20px;padding:12px 15px;margin:9px 0}[data-testid=stChatMessage]:has([data-testid=chatAvatarIcon-user]){background:var(--s);margin-left:8%}[data-testid=stChatInput]{background:white;border:1px solid #8EAF98;border-radius:18px}[data-testid=stChatInput] button{background:var(--p);color:white}.badge{background:var(--s);color:var(--p);padding:5px 10px;border-radius:999px;font-size:.78rem}@media(max-width:640px){.block-container{padding:.7rem .7rem 7rem}[data-testid=stChatMessage]{margin-left:0!important}}</style>''',unsafe_allow_html=True)
b64=base64.b64encode(open(DOG,'rb').read()).decode();st.markdown(f'<div class="head"><div class="row"><img class="mascot" src="data:image/png;base64,{b64}"><div><h1>Un espacio para escucharte</h1><p>Conversemos sobre cómo te has sentido y tu experiencia en el trabajo.</p></div></div></div>',unsafe_allow_html=True)
@st.cache_data
def datos():return pd.read_csv('data/diccionario.csv')
def add(r,c):st.session_state.msg.append({'role':r,'content':c})
def init():
 for k,v in {'etapa':'relato','msg':[],'dims':[],'sid':str(uuid.uuid4()),'prioridad':False,'frec':None,'dur':None,'imps':[],'intentos':0}.items():
  if k not in st.session_state:st.session_state[k]=v
 if not st.session_state.msg:add('assistant',BIENVENIDA)
def reset():
 for k in list(st.session_state.keys()):st.session_state.pop(k,None)
 st.rerun()
init();df=datos()
with st.expander('Participación y uso de la información',expanded=not st.session_state.get('participa',False)):
 st.checkbox('Acepto participar voluntariamente en esta demostración.',key='participa')
 st.checkbox('Autorizo enviar a Gemini fragmentos sin identificadores para comprender y redactar respuestas.',key='autoriza_ia',disabled=not ia_disponible())
 if not ia_disponible():st.caption('Gemini no está configurado. Agrega GEMINI_API_KEY en Streamlit Secrets.')
if not st.session_state.get('participa'):st.stop()
a,b=st.columns([5,1])
with a:st.markdown(f'<span class="badge">Etapa: {st.session_state.etapa.replace("_"," ").title()} · IA {"activa" if ia_disponible() and st.session_state.get("autoriza_ia") else "inactiva"}</span>',unsafe_allow_html=True)
with b:st.button('Reiniciar',on_click=reset,use_container_width=True)
for m in st.session_state.msg:
 with st.chat_message(m['role'],avatar=DOG if m['role']=='assistant' else HUMAN):st.write(m['content'])
x=st.chat_input('Cuéntame con tus propias palabras...',max_chars=1800)
if x:
 add('user',x)
 if detectar_prioridad(x):st.session_state.prioridad=True;st.session_state.etapa='apoyo_prioritario';add('assistant',PRIORIDAD);st.rerun()
 if st.session_state.prioridad:
  q=norm(x)
  if q.startswith('si'):add('assistant',PELIGRO);st.session_state.prioridad=False;st.session_state.etapa='fin'
  elif q.startswith('no'):add('assistant',NO_PELIGRO);st.session_state.prioridad=False;st.session_state.etapa='contexto'
  else:add('assistant','Necesito confirmar algo importante: ¿estás en peligro inmediato? Responde **sí** o **no**.')
  st.rerun()
 e=st.session_state.etapa;anon=anonimizar(x);ia=interpretar(anon,e,{'dimensiones':st.session_state.dims,'frecuencia':st.session_state.frec,'duracion':st.session_state.dur}) if ia_disponible() and st.session_state.get('autoriza_ia') else None
 if e=='relato':
  respuesta=ia.respuesta_empatica if ia and ia.respuesta_empatica else 'Gracias por contármelo. ¿Consideras que esto se relaciona principalmente con el trabajo, con una situación personal, con ambas cosas o todavía no lo tienes claro?'
  add('assistant',respuesta);st.session_state.etapa='relacion_laboral'
 elif e=='relacion_laboral':
  r=ia.relacion_laboral if ia else relacion(x)
  if r=='personal':add('assistant',INSUFICIENTE);st.session_state.etapa='fin'
  elif r=='incierta':add('assistant',ia.pregunta_siguiente if ia and ia.pregunta_siguiente else 'Está bien no tenerlo claro todavía. ¿Qué estaba ocurriendo justo antes de sentirte así y en qué contexto suele suceder?');st.session_state.etapa='contexto'
  else:add('assistant',ia.pregunta_siguiente if ia and ia.pregunta_siguiente else '¿Qué situación concreta del trabajo está influyendo?');st.session_state.etapa='contexto'
 elif e=='contexto':
  ds=detectar(anon,df);ds_ia=[d.nombre for d in ia.dimensiones if d.confianza>=.75] if ia else [];st.session_state.dims=list(dict.fromkeys(st.session_state.dims+ds+ds_ia))
  if st.session_state.dims:add('assistant',f"Podría haber elementos relacionados con **{', '.join(st.session_state.dims)}**. ¿Representa lo que quisiste expresar? Responde sí, parcialmente o no.\n\n_Interpretación asistida por {'reglas + IA' if ds and ds_ia else ('IA experimental' if ds_ia else 'reglas locales')}._");st.session_state.etapa='confirmar'
  else:st.session_state.intentos+=1;add('assistant',ia.pregunta_siguiente if ia and ia.pregunta_siguiente else '¿Puedes contarme un ejemplo concreto de lo que ocurre?')
 elif e=='confirmar':
  q=norm(x)
  if q.startswith('si'):add('assistant','¿Con qué frecuencia ocurre? Puedes responder con tus propias palabras.');st.session_state.etapa='frecuencia'
  else:add('assistant','Gracias por corregirme. ¿Cómo describirías el aspecto laboral principal?');st.session_state.etapa='contexto'
 elif e=='frecuencia':
  v=ia.frecuencia if ia and ia.frecuencia else frecuencia(x)
  if v:st.session_state.frec=v;add('assistant',ia.pregunta_siguiente if ia and ia.pregunta_siguiente else '¿Desde cuándo ocurre?');st.session_state.etapa='duracion'
  else:add('assistant','¿Ocurrió una vez, a veces, varias veces por semana o casi todos los días?')
 elif e=='duracion':
  v=ia.duracion if ia and ia.duracion else duracion(x)
  if v:st.session_state.dur=v;add('assistant',ia.pregunta_siguiente if ia and ia.pregunta_siguiente else '¿Cómo te ha afectado esta situación?');st.session_state.etapa='impacto'
  else:add('assistant','¿Desde hace días, semanas, meses o más de seis meses?')
 elif e=='impacto':
  v=list(ia.impactos) if ia and ia.impactos else impactos(x);st.session_state.imps=v
  r=calcular(st.session_state.frec,st.session_state.dur,v)
  tipo='acompanamiento' if r['tipo'] in ['acompanamiento','seguimiento'] else ('sin_indicadores' if r['tipo']=='sin_indicadores' else 'informacion_insuficiente')
  local={'acompanamiento':ACOMPANAMIENTO,'sin_indicadores':SIN_INDICADORES,'informacion_insuficiente':INSUFICIENTE}[tipo]
  mensaje=redactar_cierre(tipo,{'dimensiones':st.session_state.dims,'frecuencia':st.session_state.frec,'duracion':st.session_state.dur,'impactos':v}) if ia_disponible() and st.session_state.get('autoriza_ia') else None
  add('assistant',mensaje or local);st.session_state.etapa='fin'
 elif e=='fin':add('assistant','La conversación ya finalizó. Puedes usar **Reiniciar** cuando quieras volver a conversar.')
 st.rerun()
