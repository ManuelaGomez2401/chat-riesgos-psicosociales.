import streamlit as st
from datetime import datetime,timezone
def disponible():
 try:return bool(st.secrets.get('SUPABASE_URL','')) and bool(st.secrets.get('SUPABASE_KEY',''))
 except:return False
def guardar_sesion(payload):
 if not disponible():return False
 from supabase import create_client
 c=create_client(st.secrets['SUPABASE_URL'],st.secrets['SUPABASE_KEY']);p=dict(payload);p['created_at']=datetime.now(timezone.utc).isoformat();c.table('sesiones_revision').insert(p).execute();return True
