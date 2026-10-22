def calcular_orientacion(frecuencia, duracion, impacto):
    puntaje = 0

    puntaje_frecuencia = {
        "Ocurrió una vez": 0,
        "Sucede ocasionalmente": 1,
        "Sucede varias veces por semana": 2,
        "Sucede casi todos los días": 3,
    }
    puntaje_duracion = {
        "Desde hace pocos días": 0,
        "Desde hace varias semanas": 1,
        "Desde hace algunos meses": 2,
        "Desde hace más de seis meses": 3,
    }

    puntaje += puntaje_frecuencia.get(frecuencia, 0)
    puntaje += puntaje_duracion.get(duracion, 0)

    impactos_reales = [
        elemento for elemento in impacto if elemento != "Ninguno de los anteriores"
    ]
    if len(impactos_reales) == 1:
        puntaje += 1
    elif len(impactos_reales) >= 2:
        puntaje += 2

    if puntaje <= 1:
        nivel = "Orientación general"
    elif puntaje <= 4:
        nivel = "Seguimiento preventivo"
    else:
        nivel = "Contacto humano recomendado"

    return nivel, puntaje


def obtener_recomendacion(dimension, nivel, recomendaciones_df):
    coincidencias = recomendaciones_df[
        (recomendaciones_df["dimension"] == dimension)
        & (recomendaciones_df["nivel_orientativo"] == nivel)
    ]

    if coincidencias.empty:
        coincidencias = recomendaciones_df[
            (recomendaciones_df["dimension"] == "general")
            & (recomendaciones_df["nivel_orientativo"] == nivel)
        ]

    if coincidencias.empty:
        return (
            "Considera observar cómo evoluciona la situación y utilizar un canal humano "
            "de orientación si continúa o aumenta su impacto."
        )

    return str(coincidencias.iloc[0]["mensaje_usuario"])


def construir_resumen(
    dimension,
    frecuencia,
    duracion,
    impacto,
    nivel,
    recomendaciones_df,
):
    impacto_texto = ", ".join(impacto)
    recomendacion = obtener_recomendacion(
        dimension, nivel, recomendaciones_df
    )

    return (
        "**Resumen preventivo**\n\n"
        f"- Dimensión provisional: **{dimension}**\n"
        f"- Frecuencia reportada: **{frecuencia}**\n"
        f"- Duración reportada: **{duracion}**\n"
        f"- Aspectos afectados: **{impacto_texto}**\n"
        f"- Orientación experimental: **{nivel}**\n\n"
        f"{recomendacion}\n\n"
        "Esta orientación no constituye un diagnóstico ni reemplaza la aplicación "
        "formal de la Batería de Riesgo Psicosocial o la valoración de un profesional."
    )
