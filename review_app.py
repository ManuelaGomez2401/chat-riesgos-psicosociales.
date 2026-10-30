import pandas as pd
import streamlit as st
from src.storage import configurado, cliente, listar_propuestas, aprobar_propuesta_completa, rechazar_propuesta_completa

st.set_page_config(page_title='Revisión académica',page_icon='🔒',layout='wide')
st.title('Módulo de aprobación de expresiones')
st.caption('Las expresiones permanecen pendientes y no entran al diccionario activo hasta ser aprobadas.')
password=st.text_input('Contraseña de revisión',type='password')
if password!=st.secrets.get('REVIEW_PASSWORD',''):st.stop()
if not configurado(admin=True):st.error('Falta SUPABASE_SERVICE_ROLE_KEY en Secrets.');st.stop()
admin=cliente(admin=True)
pend,dict_tab,hist=st.tabs(['Pendientes','Diccionario activo','Historial'])
with pend:
    propuestas=listar_propuestas('pending')
    st.metric('Pendientes',len(propuestas))
    if not propuestas:st.success('No hay propuestas pendientes.')
    for p in propuestas:
        with st.container(border=True):
            st.write(f"**Expresión:** {p['expression']}")
            st.write('**Dimensiones sugeridas:**',p.get('dimensions',[]))
            st.caption('Evidencia anonimizada: '+str(p.get('evidence','')))
            dimension=st.text_input('Dimensión aprobada',value=(p.get('dimensions') or [''])[0],key=f"d{p['id']}")
            variants=st.text_input('Variantes separadas por |',key=f"v{p['id']}")
            question=st.text_input('Pregunta aclaratoria',value='¿Qué ocurrió exactamente y en qué contexto?',key=f"q{p['id']}")
            reviewer=st.text_input('Revisado por',value='equipo académico',key=f"r{p['id']}")
            c1,c2=st.columns(2)
            if c1.button('Aprobar e incorporar',key=f"a{p['id']}",use_container_width=True):
                if not dimension.strip():st.error('La dimensión es obligatoria.')
                else:aprobar_propuesta_completa(p['id'],p['expression'],variants,dimension,question,reviewer);st.rerun()
            if c2.button('Rechazar',key=f"x{p['id']}",use_container_width=True):rechazar_propuesta_completa(p['id'],reviewer);st.rerun()
with dict_tab:
    rows=admin.table('dictionary_entries').select('*').order('created_at',desc=True).execute().data
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
with hist:
    rows=admin.table('dictionary_proposals').select('*').neq('status','pending').order('reviewed_at',desc=True).execute().data
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
