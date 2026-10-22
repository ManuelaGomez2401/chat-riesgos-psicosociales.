import os
from datetime import datetime, timezone
import streamlit as st


def supabase_configurado():
    try:
        return bool(st.secrets.get("SUPABASE_URL")) and bool(st.secrets.get("SUPABASE_KEY"))
    except Exception:
        return False


def guardar_resultado(registro):
    if not supabase_configurado():
        return False, "Modo demostración: no se guardaron datos persistentes."
    from supabase import create_client
    cliente = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    payload = dict(registro)
    payload["created_at"] = datetime.now(timezone.utc).isoformat()
    cliente.table("resultados_prueba").insert(payload).execute()
    return True, "Resultado anónimo guardado."


def obtener_resultados():
    if not supabase_configurado():
        return []
    from supabase import create_client
    cliente = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    return cliente.table("resultados_prueba").select("*").execute().data
