import base64
import pandas as pd
import streamlit as st
from src.anonymizer import anonimizar
from src.ai_budget import MAX_CALLS_PER_MONTH, MAX_CALLS_PER_SESSION, monthly_calls, can_call
from src.gemini import disponible as ia_disponible, analizar
from src.local import norm, relacion, detectar, frecuencia, duracion, impactos
from src.messages import BIENVENIDA, SIN_INDICADORES, ACOMPANAMIENTO
from src.orientation import calcular
from src.safety import detectar_prioridad, PRIORIDAD
from src.storage import (
    configurado, crear_sesion, guardar_mensaje, guardar_resultado,
    crear_propuesta, diccionario_activo, prueba_conexion,
    propuestas_pendientes, aprobar_propuesta, rechazar_propuesta,
)

DOG='assets/perrito.png'; HUMAN='assets/persona.png'; VERSION='5.2-academica'
st.set_page_config(page_title='Conversemos',page_icon='🐾',layout='centered')
st.markdown(r'''<style>
:root{--p:#527A61;--s:#EAF3EC;--d:#294B3E;--b:#CFE0D4;--w:#FFFDF9;--m:#73867C}.stApp{background:linear-gradient(180deg,#DDECE1,#F7FAF8 260px)}.block-container{max-width:900px;padding-top:1rem;padding-bottom:7rem}.hero{background:linear-gradient(135deg,#466B54,#8EAF98);color:white;border-radius:24px;padding:22px;margin-bottom:14px}.hero h1{color:white;margin:0;font-size:1.8rem}.hero p{margin:.35rem 0 0;line-height:1.5}.hero-row{display:flex;align-items:center;gap:16px}.hero img{width:68px;height:68px;border-radius:50%;border:3px solid white;object-fit:cover}.info-card{background:#FFFDF9;border:1px solid var(--b);border-radius:16px;padding:14px 16px;margin:10px 0;color:var(--d)}.consent-note{color:var(--m);font-size:.86rem;margin:-4px 0 10px 38px;line-height:1.4}[data-testid=stChatMessage]{background:var(--w);border:1px solid var(--b);border-radius:20px;padding:12px 15px}[data-testid=stChatMessage]:has([data-testid=chatAvatarIcon-user]){background:var(--s);margin-left:8%}.status{background:var(--s);color:var(--p);border-radius:999px;padding:5px 10px;font-size:.78rem;display:inline-block}@media(max-width:640px){.hero{padding:16px}.hero h1{font-size:1.4rem}.hero img{width:54px;height:54px}[data-testid=stChatMessage]{margin-left:0!important}}
</style>''',unsafe_allow_html=True)

b64=base64.b64encode(open(DOG,'rb').read()).decode()
st.markdown(f'''<div class="hero"><div class="hero-row"><img src="data:image/png;base64,{b64}"><div><h1>Conversemos</h1><p>Un chat conversacional académico para escribir lo que estás viviendo y comprender, paso a paso, si alguna situación de tu entorno laboral puede estar influyendo en tu bienestar.</p></div></div></div><div class="info-card"><b>¿Qué puedes hacer aquí?</b><br>Puedes escribir con tus propias palabras. El chat te hará preguntas para entender el contexto, la frecuencia, el tiempo y el impacto. Este espacio busca ofrecer una primera orientación preventiva; no realiza diagnósticos ni reemplaza a profesionales.</div>''',unsafe_allow_html=True)

@st.cache_data(ttl=60)
def cargar_diccionario():
    if configurado():
        try:
            rows=diccionario_activo()
            if rows:return pd.DataFrame([{'expresion':r['expression'],'variantes':r['variants'],'dimension':r['dimension'],'pregunta':r['question']} for r in rows])
        except Exception: pass
    return pd.read_csv('data/diccionario_respaldo.csv')

def add(role,text,used_ai=False):
    st.session_state.msg.append({'role':role,'content':text})
    if st.session_state.get('db_session') and st.session_state.get('autoriza_guardado'):
        try:
            guardar_mensaje({'session_id':st.session_state.db_session,'role':role,'anonymized_text':anonimizar(text),'stage':st.session_state.etapa,'used_ai':used_ai,'sequence_no':len(st.session_state.msg)})
        except Exception as exc:
            st.session_state.storage_error=str(exc)

def init():
    defaults={'etapa':'relato','msg':[],'dims':[],'frec':None,'dur':None,'imps':[],'db_session':None,'prioridad':False,'gemini_calls':0,'storage_error':None}
    for k,v in defaults.items():
        if k not in st.session_state:st.session_state[k]=v
    if not st.session_state.msg:add('assistant',BIENVENIDA)

def reset():
    for k in list(st.session_state.keys()):st.session_state.pop(k,None)
    st.rerun()

def review_panel():
    st.subheader('Módulo académico de aprobación')
    st.caption('Las propuestas no pasan directamente al diccionario. Permanecen pendientes hasta que una persona autorizada las aprueba o rechaza.')
    password=st.text_input('Contraseña de revisión',type='password',key='inline_review_password')
    if not password or password!=st.secrets.get('REVIEW_PASSWORD',''):
        st.info('Ingresa la contraseña de revisión para ver propuestas pendientes.')
        return
    if not configurado(admin=True):
        st.error('Falta SUPABASE_SERVICE_ROLE_KEY en Secrets.')
        return
    proposals=propuestas_pendientes()
    st.metric('Propuestas pendientes',len(proposals))
    if not proposals:
        st.success('No hay propuestas pendientes de revisión.')
        return
    for p in proposals:
        with st.container(border=True):
            st.write(f"**Expresión propuesta:** {p['expression']}")
            st.write('**Dimensiones sugeridas:**',p.get('dimensions',[]))
            st.caption('Evidencia anonimizada: '+str(p.get('evidence','')))
            dim=st.text_input('Dimensión aprobada',value=(p.get('dimensions') or [''])[0],key=f"dim_{p['id']}")
            variants=st.text_input('Variantes separadas por |',key=f"var_{p['id']}")
            question=st.text_input('Pregunta aclaratoria',value='¿Puedes contarme un ejemplo concreto?',key=f"q_{p['id']}")
            c1,c2=st.columns(2)
            if c1.button('Aprobar e incorporar',key=f"approve_{p['id']}"):
                aprobar_propuesta(p['id'],p['expression'],variants,dim,question)
                st.cache_data.clear();st.rerun()
            if c2.button('Rechazar',key=f"reject_{p['id']}"):
                rechazar_propuesta(p['id']);st.rerun()

init(); df=cargar_diccionario()
mode=st.sidebar.radio('Vista académica',['Chat conversacional','Aprobación de expresiones'])
if mode=='Aprobación de expresiones':
    review_panel();st.stop()

with st.expander('Participación y uso académico',expanded=not st.session_state.get('participa',False)):
    st.checkbox('Acepto participar voluntariamente.',key='participa')
    st.markdown('<div class="consent-note">Permite iniciar la conversación. Puedes detenerte o reiniciar cuando quieras.</div>',unsafe_allow_html=True)
    st.checkbox('Autorizo guardar una copia anonimizada del chat.',key='autoriza_guardado',disabled=not configurado())
    st.markdown('<div class="consent-note">Guarda en Supabase una versión en la que correos, teléfonos, URL y algunos documentos son reemplazados. Se usa para revisión académica; no se publica directamente.</div>',unsafe_allow_html=True)
    st.checkbox('Autorizo enviar fragmentos anonimizados a Gemini.',key='autoriza_ia',disabled=not ia_disponible())
    st.markdown('<div class="consent-note">Gemini ayuda a interpretar lenguaje abierto y sugerir preguntas. No decide la orientación final. Se limita a 3 llamadas por conversación y 100 llamadas en 30 días.</div>',unsafe_allow_html=True)
    st.checkbox('Autorizo proponer expresiones anonimizadas para mejorar el diccionario.',key='autoriza_aprendizaje',disabled=not configurado())
    st.markdown('<div class="consent-note">Si aparece una frase nueva, se guarda como propuesta pendiente. No entra al diccionario hasta que sea aprobada en el módulo académico de revisión.</div>',unsafe_allow_html=True)
    if st.button('Comprobar conexión con Supabase'):
        ok,detalle=prueba_conexion();(st.success if ok else st.error)(detalle)

if not st.session_state.get('participa'):st.stop()
if st.session_state.autoriza_guardado and not st.session_state.db_session:
    try:
        creada=crear_sesion({'app_version':VERSION,'consent_store':True,'consent_ai':bool(st.session_state.autoriza_ia),'consent_learning':bool(st.session_state.autoriza_aprendizaje)})
        st.session_state.db_session=creada['id'];st.success('Guardado académico activado para esta conversación.')
    except Exception as exc:st.error(f'No fue posible iniciar el guardado en Supabase: {exc}')

c1,c2=st.columns([5,1])
with c1:
    allowed,reason=can_call() if st.session_state.autoriza_ia and ia_disponible() else (False,'IA no autorizada')
    st.markdown(f'<span class="status">Etapa: {st.session_state.etapa} · IA {st.session_state.gemini_calls}/{MAX_CALLS_PER_SESSION} · Datos {"activos" if st.session_state.db_session else "temporales"}</span>',unsafe_allow_html=True)
with c2:st.button('Reiniciar',on_click=reset)
if st.session_state.storage_error:st.warning('La conversación sigue, pero ocurrió un error de guardado: '+st.session_state.storage_error)

for m in st.session_state.msg:
    with st.chat_message(m['role'],avatar=DOG if m['role']=='assistant' else HUMAN):st.write(m['content'])
x=st.chat_input('Cuéntame con tus propias palabras...')
if x:
    add('user',x)
    if detectar_prioridad(x):st.session_state.prioridad=True;add('assistant',PRIORIDAD);st.session_state.etapa='prioridad';st.rerun()
    e=st.session_state.etapa;anon=anonimizar(x)
    ia=analizar(anon,e,{'dims':st.session_state.dims,'frec':st.session_state.frec,'dur':st.session_state.dur},st.session_state.db_session) if ia_disponible() and st.session_state.autoriza_ia else None
    if e=='relato':add('assistant','Gracias por contármelo. ¿Se relaciona con el trabajo, con algo personal, con ambas cosas o aún no lo tienes claro?',bool(ia));st.session_state.etapa='relacion'
    elif e=='relacion':
        r=ia.relacion if ia else relacion(x)
        if r=='personal':add('assistant','Gracias por compartirlo. Con lo conversado no identificamos elementos suficientes para relacionarlo con factores laborales. Este espacio está enfocado en el entorno laboral; puedes buscar un servicio de apoyo adecuado para otros aspectos de tu vida. 💚',bool(ia));st.session_state.etapa='fin'
        else:add('assistant',ia.pregunta if ia and ia.pregunta else '¿Qué situación concreta del trabajo está influyendo?',bool(ia));st.session_state.etapa='contexto'
    elif e=='contexto':
        loc=detectar(anon,df);dims=[i['dimension'] for i in loc];dims+=ia.dimensiones if ia else [];st.session_state.dims=list(dict.fromkeys(st.session_state.dims+dims))
        if st.session_state.autoriza_aprendizaje and ia and ia.expresion_nueva and st.session_state.db_session:
            try:crear_propuesta({'session_id':st.session_state.db_session,'expression':ia.expresion_nueva,'dimensions':ia.dimensiones,'evidence':anon})
            except Exception as exc:st.session_state.storage_error=str(exc)
        if st.session_state.dims:add('assistant',f"Podría haber elementos relacionados con **{', '.join(st.session_state.dims)}**. ¿Representa lo que quisiste expresar?",bool(ia));st.session_state.etapa='confirmar'
        else:add('assistant',ia.pregunta if ia and ia.pregunta else '¿Puedes contar un ejemplo concreto?',bool(ia))
    elif e=='confirmar':
        if norm(x).startswith('si'):add('assistant','¿Con qué frecuencia ocurre?');st.session_state.etapa='frecuencia'
        else:add('assistant','Gracias por corregirme. ¿Cómo describirías el aspecto laboral principal?');st.session_state.etapa='contexto'
    elif e=='frecuencia':
        v=ia.frecuencia if ia and ia.frecuencia else frecuencia(x)
        if v:st.session_state.frec=v;add('assistant','¿Desde cuándo ocurre?',bool(ia));st.session_state.etapa='duracion'
        else:add('assistant','¿Ocurrió una vez, a veces, varias veces por semana o casi todos los días?')
    elif e=='duracion':
        v=ia.duracion if ia and ia.duracion else duracion(x)
        if v:st.session_state.dur=v;add('assistant','¿Cómo te ha afectado?',bool(ia));st.session_state.etapa='impacto'
        else:add('assistant','¿Desde hace días, semanas, meses o más de seis meses?')
    elif e=='impacto':
        v=ia.impactos if ia and ia.impactos else impactos(x);st.session_state.imps=v;r=calcular(st.session_state.frec,st.session_state.dur,v);msg=SIN_INDICADORES if r['tipo']=='sin_indicadores' else ACOMPANAMIENTO;add('assistant',msg,bool(ia));st.session_state.etapa='fin'
        if st.session_state.db_session:
            try:guardar_resultado({'session_id':st.session_state.db_session,'relationship':'laboral','dimensions':st.session_state.dims,'frequency':st.session_state.frec,'duration':st.session_state.dur,'impacts':v,'orientation':r['tipo'],'rule_version':r['version']})
            except Exception as exc:st.session_state.storage_error=str(exc)
    elif e=='prioridad':add('assistant','Utiliza los canales indicados y busca compañía de una persona de confianza. Esta herramienta no puede continuar con una evaluación laboral en este momento.')
    elif e=='fin':add('assistant','La conversación terminó. Puedes reiniciar cuando quieras.')
    st.rerun()
