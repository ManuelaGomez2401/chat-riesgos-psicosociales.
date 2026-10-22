import json
import streamlit as st

DIMENSIONES = [
    "carga laboral", "jornada y desconexión", "relaciones y liderazgo",
    "apoyo social y liderazgo", "reconocimiento laboral", "claridad del rol",
    "autonomía y control", "seguridad laboral", "relaciones laborales",
]

def disponible():
    try:
        return bool(st.secrets.get("GEMINI_API_KEY", ""))
    except Exception:
        return False

def interpretar(texto):
    if not disponible():
        return None
    from google import genai
    cliente = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    prompt = f"""
Analiza este mensaje como apoyo experimental para una herramienta académica sobre experiencias laborales.
No diagnostiques. No confirmes acoso. No des consejo médico. No asumas que el trabajo es la causa.
Devuelve SOLO JSON válido con esta forma:
{{"dimensiones": [], "pregunta_aclaratoria": "", "resumen_neutral": ""}}
Dimensiones permitidas: {DIMENSIONES}
Mensaje sin identificadores: {texto[:1200]}
"""
    try:
        respuesta = cliente.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        limpio = respuesta.text.strip().replace("```json", "").replace("```", "").strip()
        datos = json.loads(limpio)
        datos["dimensiones"] = [
            d for d in datos.get("dimensiones", []) if d in DIMENSIONES
        ][:3]
        return datos
    except Exception:
        return None
