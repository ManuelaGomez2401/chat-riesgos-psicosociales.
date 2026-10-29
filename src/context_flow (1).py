"""Flujo contextual: Gemini profundiza una vez y luego el chat avanza."""
from src.local import norm


def texto_es_suficiente(texto):
    """Considera suficiente un relato con conducta/condición + detalle mínimo."""
    t = norm(texto)
    palabras = t.split()
    marcadores = [
        "persigue", "hostiga", "acosa", "grita", "humilla", "insinua",
        "toca", "horario", "jornada", "trabajo", "tareas", "jefe", "jefa",
        "supervisor", "coordinador", "comentarios", "amenaza", "ignora",
        "excluye", "carga", "turno", "comodin", "achantado", "achantada",
    ]
    return len(palabras) >= 6 and any(m in t for m in marcadores)


def construir_pregunta_contextual(ia, dimensiones):
    if ia and ia.pregunta:
        return ia.pregunta
    if "relaciones y liderazgo" in dimensiones:
        return "¿Qué conducta ocurrió, cuándo suele pasar y qué efecto ha tenido en ti?"
    if "carga laboral" in dimensiones:
        return "¿Qué tareas o plazos concretos están generando esa presión?"
    if "jornada y desconexión" in dimensiones:
        return "¿Qué ocurre con tus horarios, pausas o tiempo fuera de la jornada?"
    return "¿Qué ocurrió exactamente y en qué contexto suele suceder?"


def expresion_para_propuesta(texto_anonimo, ia, hubo_coincidencia_local):
    """Crea propuesta si la frase no estaba en el diccionario y la IA sí la entendió."""
    if hubo_coincidencia_local or not ia or not ia.dimensiones:
        return None
    expresion = (ia.expresion_nueva or texto_anonimo).strip()
    if len(expresion) < 4:
        return None
    return expresion[:220]
