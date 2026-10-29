import uuid
import streamlit as st


def configurado(admin=False):
    try:
        key = "SUPABASE_SERVICE_ROLE_KEY" if admin else "SUPABASE_ANON_KEY"
        return bool(st.secrets.get("SUPABASE_URL", "")) and bool(st.secrets.get(key, ""))
    except Exception:
        return False


def cliente(admin=False):
    from supabase import create_client
    key = "SUPABASE_SERVICE_ROLE_KEY" if admin else "SUPABASE_ANON_KEY"
    return create_client(st.secrets["SUPABASE_URL"], st.secrets[key])


def crear_sesion(payload):
    # Generamos el UUID en la aplicación. Así no necesitamos SELECT/RETURNING
    # sobre sessions, que está bloqueado por RLS para el rol público.
    session_id = str(uuid.uuid4())
    registro = dict(payload)
    registro["id"] = session_id
    registro["public_code"] = str(uuid.uuid4())
    cliente().table("sessions").insert(registro, returning="minimal").execute()
    return {"id": session_id, "public_code": registro["public_code"]}


def guardar_mensaje(payload):
    return cliente().table("messages").insert(payload, returning="minimal").execute()


def guardar_resultado(payload):
    # En el flujo actual solo se escribe un resultado por sesión.
    # insert evita requerir una política UPDATE, necesaria para upsert.
    return cliente().table("results").insert(payload, returning="minimal").execute()


def guardar_feedback(payload):
    return cliente().table("feedback").insert(payload, returning="minimal").execute()


def crear_propuesta(payload):
    return cliente().table("dictionary_proposals").insert(payload, returning="minimal").execute()


def diccionario_activo():
    return cliente().table("dictionary_entries").select("*").eq("status", "active").execute().data


def prueba_conexion():
    """Devuelve (True, detalle) si el diccionario puede leerse."""
    if not configurado():
        return False, "Faltan SUPABASE_URL o SUPABASE_ANON_KEY."
    try:
        data = diccionario_activo()
        return True, f"Conexión correcta. Entradas activas: {len(data)}"
    except Exception as exc:
        return False, str(exc)


def propuestas_pendientes():
    return cliente(admin=True).table("dictionary_proposals").select("*").eq("status", "pending").order("created_at").execute().data


def aprobar_propuesta(proposal_id, expression, variants, dimension, question, reviewer="equipo académico"):
    admin = cliente(admin=True)
    admin.table("dictionary_entries").upsert(
        {
            "expression": expression,
            "variants": variants,
            "dimension": dimension,
            "question": question,
            "status": "active",
            "source": "reviewed_chat",
            "reviewed_by": reviewer,
        },
        on_conflict="expression",
    ).execute()
    admin.table("dictionary_proposals").update(
        {"status": "approved", "reviewed_by": reviewer}
    ).eq("id", proposal_id).execute()


def rechazar_propuesta(proposal_id, reviewer="equipo académico"):
    cliente(admin=True).table("dictionary_proposals").update(
        {"status": "rejected", "reviewed_by": reviewer}
    ).eq("id", proposal_id).execute()
