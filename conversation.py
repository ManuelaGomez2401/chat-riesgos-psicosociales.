from src.local import relacion, detectar, frecuencia, duracion, impactos, norm

def interpretar_relacion_local(texto): return relacion(texto)
def analizar_contexto_local(texto, diccionario): return detectar(texto, diccionario)
def interpretar_frecuencia_local(texto): return frecuencia(texto)
def interpretar_duracion_local(texto): return duracion(texto)
def interpretar_impactos_local(texto): return impactos(texto)
def es_correccion(texto):
    t=norm(texto)
    return any(x in t for x in ["no es eso","no quise decir","entendiste mal","quiero corregir","eso no","me refiero a","no representa"])
