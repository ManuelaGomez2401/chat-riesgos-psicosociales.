# Conversemos V6 integrada

## Incluye
- Gemini entra directamente en la etapa `contexto` después de que la persona indica relación laboral/mixta/incierta y describe la situación. Clasifica solo en dimensiones permitidas y formula una pregunta natural; no vuelve a preguntar si la situación es laboral.
- El protocolo prioritario no pide reiniciar. Mantiene botones `tel:106` y `tel:123`, que abren el marcador sin realizar la llamada automáticamente.
- Asistencia emocional local, sin Gemini, basada en `data/diccionario_bienestar_psicologico_con_asistencia.xlsx`.
- El final desactiva la caja de entrada, por lo que no entra en bucle.
- `review_app.py` funciona como aplicación privada separada para aprobar/rechazar expresiones con la clave privada de Supabase.
- Propuestas nuevas quedan `pending`; no se incorporan al diccionario hasta aprobación.

## Despliegue
- App pública: `app.py`
- App privada de revisión: `review_app.py`
- Secrets requeridos: `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `REVIEW_PASSWORD`.

## Nota de seguridad
La Línea 106 ofrece orientación en salud mental; ante peligro inmediato debe usarse el 123 o urgencias. El proyecto es académico y no diagnostica.
