from datetime import datetime, timezone
import streamlit as st

def disponible():
    try:
        return bool(st.secrets.get("SUPABASE_URL", "")) and bool(st.secrets.get("SUPABASE_KEY", ""))
    except Exception:
        return False

def guardar(payload):
    if not disponible():
        return False
    from supabase import create_client
    cliente = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    registro = dict(payload)
    registro["created_at"] = datetime.now(timezone.utc).isoformat()
    cliente.table("sesiones_revision").insert(registro).execute()
    return True
