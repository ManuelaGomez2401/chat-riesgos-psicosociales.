import os
import streamlit as st
from src.storage import configurado, cliente

# Límites conservadores para el prototipo académico.
MAX_CALLS_PER_SESSION = 3
MAX_CALLS_PER_MONTH = 100
MAX_INPUT_CHARS = 2500
MAX_OUTPUT_TOKENS = 180
MODEL_NAME = "gemini-2.5-flash"


def _session_calls():
    return int(st.session_state.get("gemini_calls", 0))


def monthly_calls():
    if not configurado(admin=True):
        # Sin contador global confiable, no habilitamos llamadas pagas.
        return None
    try:
        response = (
            cliente(admin=True)
            .table("gemini_usage")
            .select("id", count="exact")
            .gte("created_at", "now() - interval '30 days'")
            .execute()
        )
        return int(response.count or 0)
    except Exception:
        return None


def can_call():
    if _session_calls() >= MAX_CALLS_PER_SESSION:
        return False, "Límite de 3 llamadas de IA alcanzado en esta conversación."
    total = monthly_calls()
    if total is None:
        return False, "No se pudo verificar el límite mensual. Se utilizarán reglas locales."
    if total >= MAX_CALLS_PER_MONTH:
        return False, "Límite académico mensual de IA alcanzado. Se utilizarán reglas locales."
    return True, "IA disponible"


def prepare_text(text):
    return str(text)[:MAX_INPUT_CHARS]


def register_usage(session_id, stage, input_text, output_text, success=True):
    st.session_state.gemini_calls = _session_calls() + 1
    if configurado(admin=True):
        try:
            cliente(admin=True).table("gemini_usage").insert(
                {
                    "session_id": session_id,
                    "stage": stage,
                    "model": MODEL_NAME,
                    "input_chars": len(str(input_text)),
                    "output_chars": len(str(output_text)),
                    "success": bool(success),
                },
                returning="minimal",
            ).execute()
        except Exception:
            pass
