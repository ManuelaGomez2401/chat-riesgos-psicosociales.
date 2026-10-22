import re
import unicodedata

FRASES_PRIORITARIAS = [
    "me quiero matar", "quiero matarme", "voy a matarme", "me voy a matar",
    "quiero morir", "no quiero vivir", "me quiero suicidar", "voy a suicidarme",
    "acabar con mi vida", "quitarme la vida", "hacerme daño", "lastimarme",
    "seria mejor no despertar", "no vale la pena seguir", "quiero desaparecer para siempre",
    "acabar con todo", "ya tengo preparado como hacerlo",
]

FRASES_NEGADAS = [
    "no me quiero matar", "no quiero matarme", "no quiero morir",
    "no pienso suicidarme", "no voy a hacerme daño",
]

def normalizar(texto):
    texto = unicodedata.normalize("NFD", str(texto).lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9ñ\s]", " ", texto)).strip()

def detectar_prioridad(texto):
    t = normalizar(texto)
    if any(normalizar(frase) in t for frase in FRASES_NEGADAS):
        return False
    return any(normalizar(frase) in t for frase in FRASES_PRIORITARIAS)

RESPUESTA_PRIORITARIA = """**Siento mucho que estés pasando por esto. Gracias por decirlo. 💚**

Lo que acabas de compartir requiere apoyo inmediato y está fuera del alcance de esta herramienta. Por favor, no enfrentes este momento a solas.

**Si existe un peligro inmediato o ya has hecho algo para lastimarte, llama al 123 o dirígete al servicio de urgencias más cercano.**

En Colombia puedes marcar la **Línea 106**, gratuita y disponible las 24 horas, para recibir escucha, orientación e intervención en crisis.

Si puedes hacerlo con seguridad, comunícate ahora con una persona de confianza y dile claramente: **“Estoy en riesgo y necesito que te quedes conmigo y me ayudes a buscar atención”.**

¿Estás en peligro inmediato en este momento? Puedes responder **sí** o **no**."""

RESPUESTA_PELIGRO_INMEDIATO = """**Busca ayuda inmediata ahora.**

Llama al **123**, pide a una persona cercana que permanezca contigo o dirígete al servicio de urgencias más cercano. También puedes marcar la **Línea 106** en Colombia.

Aléjate, si puedes hacerlo con seguridad, de cualquier objeto, sustancia o lugar que pueda ponerte en peligro. Esta herramienta no puede sustituir una atención de emergencia."""

RESPUESTA_SIN_PELIGRO_INMEDIATO = """Gracias por responder. Aunque no haya un peligro inmediato, lo que compartiste merece apoyo humano hoy.

Por favor, llama a la **Línea 106** o comunícate con una persona de confianza y cuéntale claramente lo que estás viviendo. Si la situación cambia o sientes que podrías lastimarte, llama al **123** o acude a urgencias."""
