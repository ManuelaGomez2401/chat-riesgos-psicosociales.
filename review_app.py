import pandas as pd,streamlit as st
from src.storage import configurado,cliente
st.set_page_config(page_title='Revisión académica',page_icon='🔒',layout='wide')
st.title('Panel de revisión académica')
password=st.text_input('Contraseña de revisión',type='password')
if not password or password!=st.secrets.get('REVIEW_PASSWORD',''):st.stop()
if not configurado(admin=True):st.error('Falta SUPABASE_SERVICE_ROLE_KEY.');st.stop()
admin=cliente(admin=True)
tab1,tab2=st.tabs(['Conversaciones','Propuestas de diccionario'])
with tab1:
 sessions=admin.table('sessions').select('*').order('started_at',desc=True).limit(100).execute().data
 st.dataframe(pd.DataFrame(sessions),use_container_width=True)
 if sessions:
  sid=st.selectbox('Sesión',options=[s['id'] for s in sessions])
  msgs=admin.table('messages').select('*').eq('session_id',sid).order('sequence_no').execute().data
  st.dataframe(pd.DataFrame(msgs),use_container_width=True,hide_index=True)
with tab2:
 props=admin.table('dictionary_proposals').select('*').eq('status','pending').order('created_at').execute().data
 if not props:st.info('No hay propuestas pendientes.')
 for p in props:
  with st.container(border=True):
   st.write(f"**{p['expression']}**");st.write(p.get('dimensions',[]));st.caption(p.get('evidence',''))
   dimension=st.text_input('Dimensión aprobada',value=(p.get('dimensions') or [''])[0],key=f"d{p['id']}")
   variantes=st.text_input('Variantes',key=f"v{p['id']}")
   pregunta=st.text_input('Pregunta aclaratoria',value='¿Puedes contarme un ejemplo concreto?',key=f"q{p['id']}")
   c1,c2=st.columns(2)
   if c1.button('Aprobar e incorporar',key=f"a{p['id']}"):
    admin.table('dictionary_entries').upsert({'expression':p['expression'],'variants':variantes,'dimension':dimension,'question':pregunta,'status':'active','source':'reviewed_chat','reviewed_by':'equipo académico'},on_conflict='expression').execute()
    admin.table('dictionary_proposals').update({'status':'approved','reviewed_by':'equipo académico'}).eq('id',p['id']).execute();st.rerun()
   if c2.button('Rechazar',key=f"r{p['id']}"):
    admin.table('dictionary_proposals').update({'status':'rejected','reviewed_by':'equipo académico'}).eq('id',p['id']).execute();st.rerun()
