def crear(ia,mensaje):
    if not ia or not ia.expresion_nueva:return None
    return {"expresion":ia.expresion_nueva,"mensaje_origen":mensaje,"dimensiones":[d.nombre for d in ia.dimensiones],"estado":"pendiente_revision"}
