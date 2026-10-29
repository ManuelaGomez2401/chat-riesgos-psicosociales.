# Conversemos - V5.2 académica

Incluye:
- Cabecera que explica qué es el chat.
- Consentimientos explicados.
- Límites de Gemini: 3 llamadas por sesión y 100 en 30 días.
- Registro del consumo en `gemini_usage`.
- Módulo visible pero protegido para aprobar o rechazar expresiones.
- Las propuestas permanecen `pending` hasta aprobación.

## SQL adicional
Después de los scripts anteriores, ejecutar `supabase/patch_v52.sql`.
