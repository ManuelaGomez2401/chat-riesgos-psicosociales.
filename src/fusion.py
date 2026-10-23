def fusionar(locales,ia):
    if ia:
        ia_altas=[d.nombre for d in ia.dimensiones if d.confianza>=0.80]
        comunes=[d for d in locales if d in ia_altas]
        if comunes:return {"dimensiones":comunes,"fuente":"reglas + IA","pregunta":ia.pregunta_siguiente}
        if ia_altas:return {"dimensiones":ia_altas,"fuente":"IA experimental","pregunta":ia.pregunta_siguiente}
        if ia.pregunta_siguiente:return {"dimensiones":[],"fuente":"IA experimental","pregunta":ia.pregunta_siguiente}
    if locales:return {"dimensiones":locales,"fuente":"reglas locales","pregunta":"¿Esta interpretación representa lo que quisiste expresar?"}
    return {"dimensiones":[],"fuente":"pregunta de respaldo","pregunta":"¿Puedes contarme una situación concreta del trabajo, como una tarea, un horario, un trato o un cambio reciente?"}
