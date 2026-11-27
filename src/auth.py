import streamlit as st
from supabase import create_client


def _url():
    return st.secrets.get("SUPABASE_URL", "")


def _publishable_key():
    return st.secrets.get("SUPABASE_ANON_KEY", "")


def _secret_key():
    return st.secrets.get("SUPABASE_SERVICE_ROLE_KEY", "")


def client():
    if not _url() or not _publishable_key():
        raise RuntimeError("Faltan SUPABASE_URL o SUPABASE_ANON_KEY en Secrets.")
    return create_client(_url(), _publishable_key())


def admin_client():
    if not _url() or not _secret_key():
        raise RuntimeError("Falta SUPABASE_SERVICE_ROLE_KEY en Secrets.")
    return create_client(_url(), _secret_key())


def init_auth_state():
    defaults = {
        "auth_user": None,
        "auth_email": None,
        "auth_access_token": None,
        "auth_refresh_token": None,
        "auth_profile": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def is_logged_in():
    return bool(st.session_state.get("auth_user"))


def current_user_id():
    return st.session_state.get("auth_user")


def current_profile():
    return st.session_state.get("auth_profile") or {}


def current_role():
    return current_profile().get("role", "participant")


def _set_session(auth_response):
    session = auth_response.session
    user = auth_response.user
    if not session or not user:
        raise RuntimeError("Supabase no devolvió una sesión válida.")

    st.session_state.auth_user = str(user.id)
    st.session_state.auth_email = user.email
    st.session_state.auth_access_token = session.access_token
    st.session_state.auth_refresh_token = session.refresh_token

    sb = client()
    sb.postgrest.auth(session.access_token)
    profile_result = (
        sb.table("profiles")
        .select(
            "id, display_name, role, organization_code, active, "
            "birth_date, gender_identity, demographic_consent, "
            "created_at, last_login_at"
        )
        .eq("id", str(user.id))
        .single()
        .execute()
    )
    st.session_state.auth_profile = profile_result.data or {
        "id": str(user.id),
        "display_name": user.email,
        "role": "participant",
        "active": True,
    }


def sign_in(email, password):
    response = client().auth.sign_in_with_password(
        {"email": email, "password": password}
    )
    _set_session(response)
    return current_profile()


def sign_up(
    email,
    password,
    display_name,
    birth_date,
    gender_identity,
    demographic_consent,
):
    response = client().auth.sign_up(
        {
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "display_name": display_name,
                    "birth_date": birth_date.isoformat(),
                    "gender_identity": gender_identity,
                    "demographic_consent": bool(demographic_consent),
                }
            },
        }
    )
    if response.session:
        _set_session(response)
        return {"confirmed": True, "message": "Cuenta creada e iniciada."}
    return {
        "confirmed": False,
        "message": "Cuenta creada. Revisa tu correo para confirmar el registro.",
    }


def sign_out():
    try:
        if st.session_state.get("auth_access_token"):
            sb = client()
            sb.postgrest.auth(st.session_state.auth_access_token)
            sb.auth.sign_out()
    finally:
        for key in [
            "auth_user",
            "auth_email",
            "auth_access_token",
            "auth_refresh_token",
            "auth_profile",
        ]:
            st.session_state[key] = None


def authenticated_client():
    token = st.session_state.get("auth_access_token")
    if not token:
        raise RuntimeError("El usuario no ha iniciado sesión.")
    sb = client()
    sb.postgrest.auth(token)
    return sb


def update_my_profile(
    display_name,
    birth_date,
    gender_identity,
    demographic_consent,
):
    payload = {
        "display_name": display_name,
        "birth_date": birth_date.isoformat(),
        "gender_identity": gender_identity,
        "demographic_consent": bool(demographic_consent),
    }
    result = (
        authenticated_client()
        .table("profiles")
        .update(payload)
        .eq("id", current_user_id())
        .execute()
    )
    if result.data:
        st.session_state.auth_profile = result.data[0]
    return result.data


def list_profiles_admin():
    if current_role() != "admin":
        raise PermissionError("Solo un administrador puede consultar usuarios.")
    return (
        admin_client()
        .table("profiles")
        .select(
            "id, display_name, role, organization_code, active, "
            "birth_date, gender_identity, demographic_consent, "
            "created_at, last_login_at"
        )
        .order("created_at", desc=True)
        .execute()
        .data
        or []
    )


def update_profile_role_admin(user_id, role, active=True):
    if current_role() != "admin":
        raise PermissionError("Solo un administrador puede modificar roles.")
    if role not in {"participant", "reviewer", "admin"}:
        raise ValueError("Rol inválido.")
    return (
        admin_client()
        .table("profiles")
        .update({"role": role, "active": bool(active)})
        .eq("id", user_id)
        .execute()
        .data
    )
