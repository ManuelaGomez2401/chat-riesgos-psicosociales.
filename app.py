import uuid
import pandas as pd
import streamlit as st
from src.core import detectar, relacion, frecuencia, duracion, impactos, nivel

st.set_page_config(page_title="Escucha Laboral", page_icon="💬", layout="centered")
st.markdown('''<style>
.stApp{background:linear-gradient(180deg,#f2faf8,#fff 45%)}
.block-container{max-width:850px;padding-top:1.4rem}
[data-testid="stChatMessage"]{border:1px solid #dbeae8;border-radius:20px;padding:13px 16px;margin:9px 0;box-shadow:0 5px 18px rgba(23,50,77,.06)}
.hero{padding:26px;border-radius:24px;background:linear-gradient(135deg,#17324D,#198F8A);color:white;box-shadow:0 12px 30px rgba(23,50,77,.2);margin-bottom:16px}
.hero h1{color:white;margin:0}.note{background:#fff8e8;border-left:5px solid #f4b942;padding:12px 16px;border-radius:12px;margin:14px 0}
.pill{display:inline-block;background:#dff3f0;color:#146a66;padding:5px 11px;border-radius:999px;font-size:.82rem;font-weight:700}
</style><div class="hero"><h1>💬 Escucha Laboral</h1><p>Conversación preventiva, cercana y sin diagnósticos.</p></div><div class="note"><b>Privacidad:</b> no incluyas nombres, documentos, teléfonos, correos o empresas reales.</div>''', unsafe_allow_html=True)

@st.cache_data
def datos(): return pd.read_csv("data/diccionario.csv"), pd.read_csv("data/recomendaciones.csv")
def add(role, content): st.session_state.msg.append({"role":role,"content":content})
def init():
    defaults={"etapa":"relato","msg":[],"dims":[],"sid":str(uuid.uuid4()),"intentos_contexto":0,"hallazgos_acumulados":[]}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v
    if not st.session_state.msg: add("assistant","Hola. Cuéntame con tus propias palabras cómo te has sentido y qué ha estado ocurriendo últimamente.")
def reset():
    for k in list(st.session_state.keys()):
        if k in ["etapa","msg","dims","sid","intentos_contexto","hallazgos_acumulados","frec","dur","imps"]: st.session_state.pop(k,None)
    st.rerun()
def acumular(hallazgos):
    existentes={x["dimension"] for x in st.session_state.hallazgos_acumulados}
    for h in hallazgos:
        if h["dimension"] not in existentes: st.session_state.hallazgos_acumulados.append(h); existentes.add(h["dimension"])
    st.session_state.dims=[x["dimension"] for x in st.session_state.hallazgos_acumulados]

if not st.checkbox("Comprendo que este es un prototipo académico y acepto participar voluntariamente."): st.stop()
init(); df, rec=datos(); c1,c2=st.columns([5,1])
with c1: st.markdown(f'<span class="pill">Etapa: {st.session_state.etapa.replace("_"," ").title()}</span>', unsafe_allow_html=True)
with c2: st.button("Reiniciar", on_click=reset, use_container_width=True)
for m in st.session_state.msg:
    with st.chat_message(m["role"]): st.write(m["content"])

x=st.chat_input("Escribe tu respuesta aquí...", max_chars=1400)
if x:
    x=x.strip(); add("user",x); e=st.session_state.etapa
    if e=="relato":
        acumular(detectar(x,df)); add("assistant","Gracias por contármelo. Antes de relacionarlo con el trabajo, ¿consideras que se debe principalmente al trabajo, a una situación personal, a ambas cosas o no estás seguro/a?"); st.session_state.etapa="relacion_laboral"
    elif e=="relacion_laboral":
        r=relacion(x)
        if r=="personal": add("assistant","Gracias por aclararlo. No hay elementos suficientes para relacionar la situación con factores psicosociales laborales. Esta herramienta no es un servicio de emergencia."); st.session_state.etapa="fin"
        elif r=="incierta": add("assistant","Está bien no tenerlo claro. ¿Qué estaba ocurriendo justo antes de sentirte así y en qué contexto sucede normalmente?"); st.session_state.etapa="contexto"
        elif r in ["trabajo","ambas"]: add("assistant","¿Qué situación concreta del trabajo está influyendo? Describe tareas, horarios, trato, cambios o relaciones, sin nombres."); st.session_state.etapa="contexto"
        else: add("assistant","¿Dirías que se relaciona con el trabajo, con algo personal, con ambos o aún no lo tienes claro?")
    elif e=="contexto":
        hs=detectar(x,df); acumular(hs)
        if hs:
            st.session_state.intentos_contexto=0
            dims=", ".join(st.session_state.dims)
            add("assistant",f"Podría haber elementos relacionados con {dims}. Esta interpretación es provisional. ¿Representa lo que quisiste expresar? Responde sí, parcialmente o no."); st.session_state.etapa="confirmar"
        else:
            st.session_state.intentos_contexto += 1
            if st.session_state.intentos_contexto==1: add("assistant","Aún necesito un poco más de contexto. ¿La situación se relaciona principalmente con carga de trabajo, horarios o descanso, trato recibido, apoyo, claridad de funciones, autonomía, reconocimiento o estabilidad laboral?")
            elif st.session_state.intentos_contexto==2: add("assistant","Todavía no tengo información suficiente para identificar una condición laboral específica. Puedes contar un ejemplo concreto o escribir “finalizar” para cerrar sin clasificación.")
            else: add("assistant","No fue posible identificar una condición laboral con suficiente claridad. Cerraremos sin clasificar la situación para evitar una conclusión incorrecta."); st.session_state.etapa="fin_sin_clasificar"
    elif e=="confirmar":
        q=x.lower()
        if "parcial" in q: add("assistant","¿Qué parte comprendí bien y cuál debo corregir?"); st.session_state.etapa="contexto"
        elif q.strip().startswith("no"): st.session_state.hallazgos_acumulados=[]; st.session_state.dims=[]; add("assistant","Gracias por corregirme. ¿Cómo describirías el aspecto laboral principal?"); st.session_state.etapa="contexto"
        elif "si" in q or "sí" in q: add("assistant","¿Con qué frecuencia ocurre? Escríbelo libremente, por ejemplo: “dos veces por semana” o “casi todos los días”."); st.session_state.etapa="frecuencia"
        else: add("assistant","¿La interpretación fue correcta? Responde sí, parcialmente o no.")
    elif e=="frecuencia":
        v=frecuencia(x)
        if v: st.session_state.frec=v; add("assistant","¿Desde cuándo ocurre? Por ejemplo: “hace tres semanas” o “desde hace dos meses”."); st.session_state.etapa="duracion"
        else: add("assistant","No entendí la frecuencia. ¿Ocurrió una vez, a veces, varias veces por semana o casi todos los días?")
    elif e=="duracion":
        v=duracion(x)
        if v: st.session_state.dur=v; add("assistant","¿Cómo te ha afectado? Puedes mencionar sueño, concentración, motivación, relaciones, vida personal o tareas. También puedes decir que no te ha afectado."); st.session_state.etapa="impacto"
        else: add("assistant","No entendí la duración. ¿Ocurre desde hace días, semanas, meses o más de seis meses?")
    elif e=="impacto":
        v=impactos(x)
        if v:
            st.session_state.imps=v; n=nivel(st.session_state.frec,st.session_state.dur,v); dims=st.session_state.dims or ["situación laboral por aclarar"]
            match=rec[(rec.dimension.isin(dims))&(rec.nivel==n)]; match=match if not match.empty else rec[(rec.dimension=="general")&(rec.nivel==n)]
            texto=match.iloc[0].mensaje if not match.empty else "Observa la evolución y considera un canal humano si persiste."
            add("assistant",f"**Resultado preventivo provisional: {n}.**\n\nAspectos explorados: {', '.join(dims)}.\n\n{texto}\n\nNo es diagnóstico ni medición oficial. ¿Esta conclusión representa lo conversado?"); st.session_state.etapa="feedback"
        else: add("assistant","No logré identificar el impacto. ¿Ha afectado descanso, concentración, motivación, relaciones, vida personal o tareas?")
    elif e=="feedback": add("assistant","Gracias por tu retroalimentación. Puedes reiniciar cuando quieras."); st.session_state.etapa="fin"
    elif e in ["fin","fin_sin_clasificar"]: add("assistant","La conversación terminó. Usa Reiniciar para comenzar otra prueba.")
    st.rerun()
