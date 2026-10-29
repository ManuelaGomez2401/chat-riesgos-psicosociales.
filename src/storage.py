import streamlit as st

def configurado(admin=False):
 try:
  key='SUPABASE_SERVICE_ROLE_KEY' if admin else 'SUPABASE_ANON_KEY'
  return bool(st.secrets.get('SUPABASE_URL','')) and bool(st.secrets.get(key,''))
 except:return False
def cliente(admin=False):
 from supabase import create_client
 key='SUPABASE_SERVICE_ROLE_KEY' if admin else 'SUPABASE_ANON_KEY'
 return create_client(st.secrets['SUPABASE_URL'],st.secrets[key])
def crear_sesion(payload):
 return cliente().table('sessions').insert(payload).execute().data[0]
def guardar_mensaje(payload):return cliente().table('messages').insert(payload).execute()
def guardar_resultado(payload):return cliente().table('results').upsert(payload,on_conflict='session_id').execute()
def guardar_feedback(payload):return cliente().table('feedback').insert(payload).execute()
def crear_propuesta(payload):return cliente().table('dictionary_proposals').insert(payload).execute()
def diccionario_activo():return cliente().table('dictionary_entries').select('*').eq('status','active').execute().data
