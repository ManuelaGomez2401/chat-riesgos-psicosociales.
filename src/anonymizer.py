import re
PATRONES=[(re.compile(r"\b[\w.-]+@[\w.-]+\.\w+\b",re.I),"[CORREO]"),(re.compile(r"\b(?:\+57\s?)?3\d{9}\b"),"[TELÉFONO]"),(re.compile(r"https?://\S+",re.I),"[URL]"),(re.compile(r"\b(?:CC|C\.C\.|cédula)\s*[:#-]?\s*\d{6,10}\b",re.I),"[DOCUMENTO]")]
def anonimizar(texto):
    salida=str(texto)
    for patron,reemplazo in PATRONES: salida=patron.sub(reemplazo,salida)
    return salida
