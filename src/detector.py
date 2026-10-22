import re
import unicodedata
from rapidfuzz.fuzz import partial_ratio
import pandas as pd

NEGACIONES = {"no", "nunca", "jamas", "tampoco", "sin"}


def normalizar(texto):
    texto = unicodedata.normalize("NFD", str(texto).lower().strip())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^a-z0-9ñ\s]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def contiene_negacion_cercana(mensaje, expresion, ventana=3):
    palabras = normalizar(mensaje).split()
    objetivo = normalizar(expresion).split()
    if not objetivo:
        return False
    primera = objetivo[0]
    posiciones = [i for i, p in enumerate(palabras) if p == primera]
    for pos in posiciones:
        inicio = max(0, pos - ventana)
        if any(p in NEGACIONES for p in palabras[inicio:pos]):
            return True
    return False


def _expresiones_fila(fila):
    valores = [str(fila["expresion"])]
    if pd.notna(fila.get("variantes")):
        valores.extend(v.strip() for v in str(fila["variantes"]).split("|") if v.strip())
    return valores


def detectar_coincidencias(mensaje, df, umbral_fuerte=88, umbral_posible=78):
    mensaje_n = normalizar(mensaje)
    hallazgos = []

    for _, fila in df.iterrows():
        mejor = None
        for expresion in _expresiones_fila(fila):
            expresion_n = normalizar(expresion)
            exacta = expresion_n in mensaje_n
            similitud = 100 if exacta else partial_ratio(expresion_n, mensaje_n)
            negada = contiene_negacion_cercana(mensaje, expresion)

            if similitud >= umbral_posible and not negada:
                candidato = {
                    "id": str(fila["id"]),
                    "expresion": str(fila["expresion"]),
                    "coincidencia": expresion,
                    "dimension": str(fila["dimension_probable"]),
                    "pregunta": str(fila["pregunta_aclaratoria"]),
                    "ambiguedad": str(fila["ambiguedad"]),
                    "similitud": round(float(similitud), 1),
                    "tipo": "exacta" if exacta else ("fuerte" if similitud >= umbral_fuerte else "posible"),
                }
                if mejor is None or candidato["similitud"] > mejor["similitud"]:
                    mejor = candidato

        if mejor:
            hallazgos.append(mejor)

    hallazgos.sort(key=lambda x: x["similitud"], reverse=True)
    unicos = []
    dimensiones = set()
    for item in hallazgos:
        if item["dimension"] not in dimensiones:
            unicos.append(item)
            dimensiones.add(item["dimension"])
    return unicos[:3]
