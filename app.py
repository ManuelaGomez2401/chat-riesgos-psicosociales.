import base64
import pandas as pd
import streamlit as st
from src.anonymizer import anonimizar
from src.ai_budget import MAX_CALLS_PER_SESSION, can_call
from src.gemini import disponible as ia_disponible, analizar
from src.local import norm, relacion, detectar, frecuencia, duracion, impactos

# Funciones integradas en app.py para evitar errores de módulos faltantes en GitHub.
def interpretar_relacion_local(texto): return relacion(texto)
def analizar_contexto_local(texto, diccionario): return detectar(texto, diccionario)
def interpretar_frecuencia_local(texto): return frecuencia(texto)
def interpretar_duracion_local(texto): return duracion(texto)
def interpretar_impactos_local(texto): return impactos(texto)
def es_correccion(texto):
    t=norm(texto)
    return any(x in t for x in ["no es eso","no quise decir","entendiste mal","quiero corregir","eso no","me refiero a","no representa"])
def texto_es_suficiente(texto):
    t=norm(texto); palabras=t.split()
    marcadores=["persigue","hostiga","acosa","grita","humilla","insinua","toca","horario","jornada","trabajo","tareas","jefe","jefa","supervisor","coordinador","comentarios","amenaza","ignora","excluye","carga","turno","comodin","achantado","achantada"]
    return len(palabras)>=6 and any(m in t for m in marcadores)
def construir_pregunta_contextual(ia, dimensiones):
    if ia and ia.pregunta: return ia.pregunta
    if "relaciones y liderazgo" in dimensiones: return "¿Qué conducta ocurrió, cuándo suele pasar y qué efecto ha tenido en ti?"
    if "carga laboral" in dimensiones: return "¿Qué tareas o plazos concretos están generando esa presión?"
    if "jornada y desconexión" in dimensiones: return "¿Qué ocurre con tus horarios, pausas o tiempo fuera de la jornada?"
    return "¿Qué ocurrió exactamente y en qué contexto suele suceder?"
def expresion_para_propuesta(texto_anonimo, ia, hubo_coincidencia_local):
    if hubo_coincidencia_local or not ia or not ia.dimensiones: return None
    expresion=(ia.expresion_nueva or texto_anonimo).strip()
    return expresion[:220] if len(expresion)>=4 else None
CONTEXT_OBJECTIVE="""Analiza el relato laboral completo. Identifica hasta tres dimensiones permitidas sin diagnosticar ni confirmar acoso. Redacta UNA sola pregunta de profundización que use detalles del mensaje. No preguntes '¿representa lo que quisiste expresar?'. Si la frase es nueva o coloquial, devuelve en expresion_nueva una versión breve y reutilizable."""
from src.messages import BIENVENIDA, SIN_INDICADORES, ACOMPANAMIENTO_GENERAL, ACOMPANAMIENTO_RELACIONES, INFORMACION_INSUFICIENTE
from src.orientation import calcular
from src.safety import detectar_prioridad, PRIORIDAD
from src.storage import configurado, crear_sesion, guardar_mensaje, guardar_resultado, crear_propuesta, diccionario_activo, propuestas_pendientes, aprobar_propuesta, rechazar_propuesta

DOG='assets/perrito.png'; HUMAN='assets/persona.png'; VERSION='5.5-flujo-natural'
st.set_page_config(page_title='Conversemos',page_icon='🐾',layout='centered')
st.markdown(r'''<style>:root{--p:#527A61;--s:#EAF3EC;--d:#294B3E;--b:#CFE0D4;--w:#FFFDF9;--m:#73867C}.stApp{background:linear-gradient(180deg,#DDECE1,#F7FAF8 260px)}.block-container{max-width:900px;padding-top:1rem;padding-bottom:7rem}.hero{background:linear-gradient(135deg,#466B54,#8EAF98);color:white;border-radius:24px;padding:22px;margin-bottom:14px}.hero h1{color:white;margin:0;font-size:1.8rem}.hero p{margin:.35rem 0 0;line-height:1.5}.hero-row{display:flex;align-items:center;gap:16px}.hero img{width:68px;height:68px;border-radius:50%;border:3px solid white;object-fit:cover}.info-card{background:#FFFDF9;border:1px solid var(--b);border-radius:16px;padding:14px 16px;margin:10px 0;color:var(--d)}.consent-note{color:var(--m);font-size:.86rem;margin:-4px 0 10px 38px;line-height:1.4}[data-testid=stChatMessage]{background:var(--w);border:1px solid var(--b);border-radius:20px;padding:12px 15px}[data-testid=stChatMessage]:has([data-testid=chatAvatarIcon-user]){background:var(--s);margin-left:8%}.status{background:var(--s);color:var(--p);border-radius:999px;padding:5px 10px;font-size:.78rem;display:inline-block}@media(max-width:640px){.hero{padding:16px}.hero h1{font-size:1.4rem}.hero img{width:54px;height:54px}[data-testid=stChatMessage]{margin-left:0!important}}</style>''',unsafe_allow_html=True)
b64=base64.b64encode(open(DOG,'rb').read()).decode()
st.markdown(f'''<div class="hero"><div class="hero-row"><img src="data:image/png;base64,{b64}"><div><h1>Conversemos</h1><p>Un chat conversacional académico para escribir lo que estás viviendo y comprender, paso a paso, si una situación laboral puede estar influyendo en tu bienestar.</p></div></div></div><div class="info-card"><b>¿Qué puedes hacer aquí?</b><br>Escribe con tus propias palabras. El chat organizará lo que compartes sin diagnosticar ni reemplazar a profesionales.</div>''',unsafe_allow_html=True)

@st.cache_data(ttl=60)
def cargar_diccionario():
    if configurado():
        try:
            rows=diccionario_activo()
            if rows:return pd.DataFrame([{'expresion':r['expression'],'variantes':r['variants'],'dimension':r['dimension'],'pregunta':r['question']} for r in rows])
        except Exception:pass
    return pd.read_csv('data/diccionario_respaldo.csv')

def add(role,text,used_ai=False):
    st.session_state.msg.append({'role':role,'content':text})
    if st.session_state.get('db_session') and st.session_state.get('autoriza_guardado'):
        try:guardar_mensaje({'session_id':st.session_state.db_session,'role':role,'anonymized_text':anonimizar(text),'stage':st.session_state.etapa,'used_ai':used_ai,'sequence_no':len(st.session_state.msg)})
        except Exception as exc:st.session_state.storage_error=str(exc)

def init():
    defaults={'etapa':'relato','msg':[],'dims':[],'frec':None,'dur':None,'imps':[],'db_session':None,'prioridad':False,'gemini_calls':0,'storage_error':None,'context_attempts':0,'gemini_budget_error':None,'consentimientos_confirmados':False,'contexto_ia_realizado':False,'contexto_profundizado':False}
    for k,v in defaults.items():
        if k not in st.session_state:st.session_state[k]=v
    if not st.session_state.msg:add('assistant',BIENVENIDA)

def reset():
    for k in list(st.session_state.keys()):st.session_state.pop(k,None)
    st.rerun()

def review_panel():
    st.subheader('Módulo académico de aprobación')
    st.caption('Las propuestas permanecen pendientes hasta que una persona autorizada las aprueba o rechaza.')
    password=st.text_input('Contraseña de revisión',type='password')
    if not password or password!=st.secrets.get('REVIEW_PASSWORD',''):st.info('Ingresa la contraseña de revisión.');return
    if not configurado(admin=True):st.error('Falta la clave privada de Supabase.');return
    proposals=propuestas_pendientes();st.metric('Propuestas pendientes',len(proposals))
    for p in proposals:
        with st.container(border=True):
            st.write(f"**{p['expression']}**");st.write(p.get('dimensions',[]));st.caption(str(p.get('evidence','')))
            dim=st.text_input('Dimensión',value=(p.get('dimensions') or [''])[0],key=f"d{p['id']}")
            variants=st.text_input('Variantes con |',key=f"v{p['id']}")
            question=st.text_input('Pregunta',value='¿Puedes contarme un ejemplo concreto?',key=f"q{p['id']}")
            c1,c2=st.columns(2)
            if c1.button('Aprobar',key=f"a{p['id']}"):aprobar_propuesta(p['id'],p['expression'],variants,dim,question);st.cache_data.clear();st.rerun()
            if c2.button('Rechazar',key=f"r{p['id']}"):rechazar_propuesta(p['id']);st.rerun()

init();df=cargar_diccionario()
mode=st.sidebar.radio('Vista académica',['Chat conversacional','Aprobación de expresiones'])
if mode=='Aprobación de expresiones':review_panel();st.stop()
with st.expander('Participación y uso académico',expanded=not st.session_state.consentimientos_confirmados):
    st.markdown('**Revisa cada opción.** Solo la participación es obligatoria; las demás son opcionales.')
    st.checkbox('Acepto participar voluntariamente.',key='participa');st.markdown('<div class="consent-note">Permite iniciar. Puedes detenerte o reiniciar.</div>',unsafe_allow_html=True)
    st.checkbox('Autorizo guardar una copia anonimizada del chat.',key='autoriza_guardado',disabled=not configurado());st.markdown('<div class="consent-note">Guarda una copia académica con reemplazo básico de correos, teléfonos, URL y algunos documentos.</div>',unsafe_allow_html=True)
    st.checkbox('Autorizo enviar fragmentos anonimizados a Gemini.',key='autoriza_ia',disabled=not ia_disponible());st.markdown('<div class="consent-note">Gemini solo se usa cuando las reglas no comprenden. Máximo 3 llamadas por conversación.</div>',unsafe_allow_html=True)
    st.checkbox('Autorizo proponer expresiones anonimizadas para mejorar el diccionario.',key='autoriza_aprendizaje',disabled=not configurado());st.markdown('<div class="consent-note">La propuesta queda pendiente y requiere aprobación humana.</div>',unsafe_allow_html=True)
    if st.button('Revisé las opciones y deseo iniciar',type='primary',use_container_width=True):
        if not st.session_state.participa:st.error('Debes aceptar la participación voluntaria.')
        else:st.session_state.consentimientos_confirmados=True;st.rerun()
if not st.session_state.consentimientos_confirmados:st.stop()
if st.session_state.autoriza_guardado and not st.session_state.db_session:
    try:st.session_state.db_session=crear_sesion({'app_version':VERSION,'consent_store':True,'consent_ai':bool(st.session_state.autoriza_ia),'consent_learning':bool(st.session_state.autoriza_aprendizaje)})['id']
    except Exception as exc:st.error(f'No fue posible iniciar el guardado: {exc}')

c1,c2=st.columns([5,1])
with c1:st.markdown(f'<span class="status">Etapa: {st.session_state.etapa} · IA {st.session_state.gemini_calls}/{MAX_CALLS_PER_SESSION} · Datos {"activos" if st.session_state.db_session else "temporales"}</span>',unsafe_allow_html=True)
with c2:st.button('Reiniciar',on_click=reset)
for m in st.session_state.msg:
    with st.chat_message(m['role'],avatar=DOG if m['role']=='assistant' else HUMAN):st.write(m['content'])

x=st.chat_input('Cuéntame con tus propias palabras...')
if x:
    add('user',x)
    if detectar_prioridad(x):st.session_state.prioridad=True;add('assistant',PRIORIDAD);st.session_state.etapa='prioridad';st.rerun()
    e=st.session_state.etapa;anon=anonimizar(x)
    if e=='relato':
        add('assistant','Gracias por contármelo. ¿Se relaciona con el trabajo, con algo personal, con ambas cosas o aún no lo tienes claro?');st.session_state.etapa='relacion'
    elif e=='relacion':
        r=interpretar_relacion_local(x);ia=None
        if r is None and ia_disponible() and st.session_state.autoriza_ia:ia=analizar(anon,e,{'objetivo':'relación'},st.session_state.db_session);r=ia.relacion if ia else None
        if r=='personal':add('assistant','Gracias por compartirlo. Con lo conversado no identificamos elementos suficientes para relacionarlo con factores laborales. Puedes buscar apoyo adecuado para otros aspectos de tu vida. 💚',bool(ia));st.session_state.etapa='fin'
        elif r=='incierta':add('assistant','Está bien no tenerlo claro. ¿Qué estaba ocurriendo justo antes y en qué contexto suele suceder?',bool(ia));st.session_state.etapa='contexto'
        else:add('assistant','¿Qué situación concreta del trabajo está influyendo?',bool(ia));st.session_state.etapa='contexto'
    elif e=='contexto':
        # En contexto, Gemini sí aporta valor: interpreta lenguaje coloquial y redacta
        # una pregunta específica. Solo se usa una vez para no gastar las 3 llamadas.
        loc=analizar_contexto_local(anon,df)
        dims_locales=[i['dimension'] for i in loc]
        ia=None
        if ia_disponible() and st.session_state.autoriza_ia and not st.session_state.contexto_ia_realizado:
            ia=analizar(
                anon,
                e,
                {'objetivo':CONTEXT_OBJECTIVE,'dims_locales':dims_locales,'dims_previas':st.session_state.dims},
                st.session_state.db_session,
            )
            st.session_state.contexto_ia_realizado=True
        dims_ia=ia.dimensiones if ia else []
        dimensiones=list(dict.fromkeys(st.session_state.dims+dims_locales+dims_ia))
        st.session_state.dims=dimensiones

        # Una expresión nueva nunca entra directamente al diccionario. Se crea una
        # propuesta pending cuando no hubo coincidencia local y Gemini sí entendió.
        propuesta=expresion_para_propuesta(anon,ia,bool(loc))
        if st.session_state.autoriza_aprendizaje and propuesta and st.session_state.db_session:
            try:
                crear_propuesta({
                    'session_id':st.session_state.db_session,
                    'expression':propuesta,
                    'dimensions':dims_ia,
                    'evidence':anon,
                })
            except Exception as exc:
                st.session_state.storage_error=str(exc)

        if dimensiones and not st.session_state.contexto_profundizado:
            # Primera respuesta contextual: Gemini hace una pregunta natural usando
            # el relato. No hay confirmación mecánica de la dimensión.
            pregunta=construir_pregunta_contextual(ia,dimensiones)
            add(
                'assistant',
                f"Gracias por explicarlo. Lo que compartes puede relacionarse provisionalmente con **{', '.join(dimensiones)}**; esto no confirma acoso ni una conclusión legal.\n\n{pregunta}",
                bool(ia),
            )
            st.session_state.contexto_profundizado=True
        elif dimensiones and st.session_state.contexto_profundizado:
            # Con la segunda respuesta de contexto ya se avanza. No se vuelve a pedir
            # validación ni se consume otra llamada de Gemini.
            add('assistant','Gracias por ampliar la situación. ¿Con qué frecuencia ocurre?')
            st.session_state.etapa='frecuencia'
        else:
            st.session_state.context_attempts+=1
            if texto_es_suficiente(anon):
                # Si el relato contiene hechos suficientes pero ni reglas ni IA dieron
                # dimensión, se avanza sin forzar una clasificación.
                add('assistant','Gracias por describir la situación. Continuemos sin asignar una categoría por ahora. ¿Con qué frecuencia ocurre?')
                st.session_state.etapa='frecuencia'
            elif st.session_state.context_attempts==1:
                add('assistant','¿Qué ocurrió exactamente, cuándo suele pasar y qué efecto ha tenido en ti?',bool(ia))
            elif st.session_state.context_attempts==2:
                add('assistant','Puedes contar un último ejemplo concreto o escribir **finalizar**. No es necesario usar palabras técnicas.')
            else:
                add('assistant',INFORMACION_INSUFICIENTE)
                st.session_state.etapa='fin'
    elif e=='frecuencia':
        if es_correccion(x):st.session_state.dims=[];st.session_state.contexto_ia_realizado=False;st.session_state.contexto_profundizado=False;add('assistant','Claro. Cuéntame cómo describirías mejor la situación.');st.session_state.etapa='contexto'
        else:
            v=interpretar_frecuencia_local(x);ia=None
            if not v and ia_disponible() and st.session_state.autoriza_ia:ia=analizar(anon,e,{'objetivo':'frecuencia'},st.session_state.db_session);v=ia.frecuencia if ia else None
            if v:st.session_state.frec=v;add('assistant','¿Desde cuándo ocurre?',bool(ia));st.session_state.etapa='duracion'
            else:add('assistant','¿Ocurrió una vez, ocasionalmente, varias veces por semana o casi todos los días?')
    elif e=='duracion':
        v=interpretar_duracion_local(x);ia=None
        if not v and ia_disponible() and st.session_state.autoriza_ia:ia=analizar(anon,e,{'objetivo':'duración'},st.session_state.db_session);v=ia.duracion if ia else None
        if v:st.session_state.dur=v;add('assistant','¿Cómo te ha afectado?',bool(ia));st.session_state.etapa='impacto'
        else:add('assistant','¿Desde hace días, semanas, meses o más de seis meses?')
    elif e=='impacto':
        v=interpretar_impactos_local(x);ia=None
        if not v and not any(z in norm(x) for z in ['no me afecta','ninguno','estoy bien','me siento bien']) and ia_disponible() and st.session_state.autoriza_ia:ia=analizar(anon,e,{'objetivo':'impactos explícitos'},st.session_state.db_session);v=ia.impactos if ia else []
        st.session_state.imps=v;r=calcular(st.session_state.frec,st.session_state.dur,v)
        if r['tipo']=='sin_indicadores':msg=SIN_INDICADORES
        elif not st.session_state.dims:msg=INFORMACION_INSUFICIENTE
        elif any(d in st.session_state.dims for d in ['relaciones y liderazgo','relaciones laborales']):msg=ACOMPANAMIENTO_RELACIONES
        else:msg=ACOMPANAMIENTO_GENERAL
        add('assistant',msg,bool(ia));st.session_state.etapa='fin'
        if st.session_state.db_session:
            try:guardar_resultado({'session_id':st.session_state.db_session,'relationship':'laboral','dimensions':st.session_state.dims,'frequency':st.session_state.frec,'duration':st.session_state.dur,'impacts':v,'orientation':r['tipo'],'rule_version':r['version']})
            except Exception as exc:st.session_state.storage_error=str(exc)
    elif e=='prioridad':add('assistant','Utiliza los canales indicados y busca compañía de una persona de confianza. La evaluación laboral se detiene en este momento.')
    elif e=='fin':add('assistant','La conversación terminó. Puedes reiniciar cuando quieras.')
    st.rerun()
