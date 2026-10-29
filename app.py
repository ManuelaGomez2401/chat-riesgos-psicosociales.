import base64,uuid,pandas as pd,streamlit as st
from src.anonymizer import anonimizar
from src.gemini import disponible as ia_disponible,analizar
from src.local import norm,relacion,detectar,frecuencia,duracion,impactos
from src.messages import BIENVENIDA,SIN_INDICADORES,ACOMPANAMIENTO
from src.orientation import calcular
from src.safety import detectar_prioridad,PRIORIDAD
from src.storage import configurado,crear_sesion,guardar_mensaje,guardar_resultado,crear_propuesta,diccionario_activo
DOG='assets/perrito.png';HUMAN='assets/persona.png';VERSION='5.0-academica'
st.set_page_config(page_title='Un espacio para escucharte',page_icon='🐾',layout='centered')
st.markdown('<style>.stApp{background:linear-gradient(180deg,#DDECE1,#F7FAF8 250px)}.block-container{max-width:860px;padding-bottom:7rem}[data-testid=stChatMessage]{background:#FFFDF9;border:1px solid #CFE0D4;border-radius:20px}[data-testid=stChatMessage]:has([data-testid=chatAvatarIcon-user]){background:#DDECE1;margin-left:8%}</style>',unsafe_allow_html=True)
@st.cache_data(ttl=60)
def cargar_diccionario():
 if configurado():
  try:
   rows=diccionario_activo()
   if rows:return pd.DataFrame([{'expresion':r['expression'],'variantes':r['variants'],'dimension':r['dimension'],'pregunta':r['question']} for r in rows])
  except:pass
 return pd.read_csv('data/diccionario_respaldo.csv')
def add(role,text,used_ai=False):
 st.session_state.msg.append({'role':role,'content':text});
 if st.session_state.get('db_session') and st.session_state.get('autoriza_guardado'):
  try:guardar_mensaje({'session_id':st.session_state.db_session,'role':role,'anonymized_text':anonimizar(text),'stage':st.session_state.etapa,'used_ai':used_ai,'sequence_no':len(st.session_state.msg)})
  except:pass
def init():
 for k,v in {'etapa':'relato','msg':[],'dims':[],'frec':None,'dur':None,'imps':[],'db_session':None,'prioridad':False}.items():
  if k not in st.session_state:st.session_state[k]=v
 if not st.session_state.msg:add('assistant',BIENVENIDA)
def reset():
 for k in list(st.session_state.keys()):st.session_state.pop(k,None)
 st.rerun()
init();df=cargar_diccionario()
with st.expander('Participación y uso académico',expanded=not st.session_state.get('participa',False)):
 st.checkbox('Acepto participar voluntariamente.',key='participa')
 st.checkbox('Autorizo guardar una copia anonimizada del chat.',key='autoriza_guardado',disabled=not configurado())
 st.checkbox('Autorizo enviar fragmentos anonimizados a Gemini.',key='autoriza_ia',disabled=not ia_disponible())
 st.checkbox('Autorizo proponer expresiones anonimizadas para mejorar el diccionario.',key='autoriza_aprendizaje',disabled=not configurado())
if not st.session_state.get('participa'):st.stop()
if st.session_state.autoriza_guardado and not st.session_state.db_session:
 try:st.session_state.db_session=crear_sesion({'app_version':VERSION,'consent_store':True,'consent_ai':bool(st.session_state.autoriza_ia),'consent_learning':bool(st.session_state.autoriza_aprendizaje)})['id']
 except:st.warning('No fue posible iniciar el guardado; el chat continuará sin persistencia.')
c1,c2=st.columns([5,1]);c1.caption(f'Etapa: {st.session_state.etapa} · IA {"activa" if ia_disponible() and st.session_state.autoriza_ia else "inactiva"} · Datos {"activos" if st.session_state.db_session else "temporales"}');c2.button('Reiniciar',on_click=reset)
for m in st.session_state.msg:
 with st.chat_message(m['role'],avatar=DOG if m['role']=='assistant' else HUMAN):st.write(m['content'])
x=st.chat_input('Cuéntame con tus propias palabras...')
if x:
 add('user',x)
 if detectar_prioridad(x):st.session_state.prioridad=True;add('assistant',PRIORIDAD);st.session_state.etapa='prioridad';st.rerun()
 e=st.session_state.etapa;anon=anonimizar(x);ia=analizar(anon,e,{'dims':st.session_state.dims,'frec':st.session_state.frec,'dur':st.session_state.dur}) if ia_disponible() and st.session_state.autoriza_ia else None
 if e=='relato':add('assistant','Gracias por contármelo. ¿Se relaciona con el trabajo, con algo personal, con ambas cosas o aún no lo tienes claro?');st.session_state.etapa='relacion'
 elif e=='relacion':
  r=ia.relacion if ia else relacion(x)
  if r=='personal':add('assistant','Gracias por compartirlo. Con lo conversado no identificamos elementos suficientes para relacionarlo con factores laborales. Este espacio está enfocado en el entorno laboral; puedes buscar un servicio de apoyo adecuado para otros aspectos de tu vida. 💚');st.session_state.etapa='fin'
  else:add('assistant',ia.pregunta if ia and ia.pregunta else '¿Qué situación concreta del trabajo está influyendo?');st.session_state.etapa='contexto'
 elif e=='contexto':
  loc=detectar(anon,df);dims=[i['dimension'] for i in loc];dims+=ia.dimensiones if ia else [];st.session_state.dims=list(dict.fromkeys(st.session_state.dims+dims))
  if st.session_state.autoriza_aprendizaje and ia and ia.expresion_nueva and st.session_state.db_session:
   try:crear_propuesta({'session_id':st.session_state.db_session,'expression':ia.expresion_nueva,'dimensions':ia.dimensiones,'evidence':anon})
   except:pass
  if st.session_state.dims:add('assistant',f"Podría haber elementos relacionados con **{', '.join(st.session_state.dims)}**. ¿Representa lo que quisiste expresar?");st.session_state.etapa='confirmar'
  else:add('assistant',ia.pregunta if ia and ia.pregunta else '¿Puedes contar un ejemplo concreto?')
 elif e=='confirmar':
  if norm(x).startswith('si'):add('assistant','¿Con qué frecuencia ocurre?');st.session_state.etapa='frecuencia'
  else:add('assistant','Gracias por corregirme. ¿Cómo describirías el aspecto laboral principal?');st.session_state.etapa='contexto'
 elif e=='frecuencia':
  v=ia.frecuencia if ia and ia.frecuencia else frecuencia(x)
  if v:st.session_state.frec=v;add('assistant','¿Desde cuándo ocurre?');st.session_state.etapa='duracion'
  else:add('assistant','¿Ocurrió una vez, a veces, varias veces por semana o casi todos los días?')
 elif e=='duracion':
  v=ia.duracion if ia and ia.duracion else duracion(x)
  if v:st.session_state.dur=v;add('assistant','¿Cómo te ha afectado?');st.session_state.etapa='impacto'
  else:add('assistant','¿Desde hace días, semanas, meses o más de seis meses?')
 elif e=='impacto':
  v=ia.impactos if ia and ia.impactos else impactos(x);st.session_state.imps=v;r=calcular(st.session_state.frec,st.session_state.dur,v);msg=SIN_INDICADORES if r['tipo']=='sin_indicadores' else ACOMPANAMIENTO;add('assistant',msg);st.session_state.etapa='fin'
  if st.session_state.db_session:
   try:guardar_resultado({'session_id':st.session_state.db_session,'relationship':'laboral','dimensions':st.session_state.dims,'frequency':st.session_state.frec,'duration':st.session_state.dur,'impacts':v,'orientation':r['tipo'],'rule_version':r['version']})
   except:pass
 elif e=='prioridad':add('assistant','Por favor utiliza los canales indicados y busca compañía de una persona de confianza. Esta herramienta no puede continuar con una evaluación laboral en este momento.')
 elif e=='fin':add('assistant','La conversación terminó. Puedes reiniciar cuando quieras.')
 st.rerun()
