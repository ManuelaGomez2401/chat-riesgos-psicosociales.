def calcular_orientacion(frecuencia, duracion, impactos):
    f = {"Ocurrió una vez": 0, "Sucede ocasionalmente": 1,
         "Sucede varias veces por semana": 2, "Sucede casi todos los días": 3}
    d = {"Desde hace pocos días": 0, "Desde hace varias semanas": 1,
         "Desde hace algunos meses": 2, "Desde hace más de seis meses": 3}
    reales = [x for x in impactos if x != "Ninguno de los anteriores"]
    puntaje = f.get(frecuencia, 0) + d.get(duracion, 0) + min(len(reales), 2)
    if puntaje <= 1:
        return "Orientación general", puntaje
    if puntaje <= 4:
        return "Seguimiento preventivo", puntaje
    return "Contacto humano recomendado", puntaje


def recomendacion_para(dimensiones, nivel, df):
    mensajes = []
    for dimension in dimensiones:
        match = df[(df["dimension"] == dimension) & (df["nivel_orientativo"] == nivel)]
        if not match.empty:
            mensajes.append(str(match.iloc[0]["mensaje_usuario"]))
    if not mensajes:
        match = df[(df["dimension"] == "general") & (df["nivel_orientativo"] == nivel)]
        if not match.empty:
            mensajes.append(str(match.iloc[0]["mensaje_usuario"]))
    return " ".join(dict.fromkeys(mensajes))
