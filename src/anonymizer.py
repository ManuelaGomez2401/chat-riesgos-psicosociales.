import re
P=[(re.compile(r"\b[\w.-]+@[\w.-]+\.\w+\b",re.I),"[CORREO]"),(re.compile(r"\b(?:\+57\s?)?3\d{9}\b"),"[TELÉFONO]"),(re.compile(r"https?://\S+",re.I),"[URL]"),(re.compile(r"\b(?:CC|C\.C\.|cédula)\s*[:#-]?\s*\d{6,10}\b",re.I),"[DOCUMENTO]")]
def anonimizar(x):
 y=str(x)
 for p,r in P:y=p.sub(r,y)
 return y
