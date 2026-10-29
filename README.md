# Parche V5.6: conversación contextual con Gemini

Reemplaza sobre V5.4/V5.5:
- `app.py`
- `src/conversation.py`

Agrega:
- `src/context_flow.py`
- `src/gemini_context_patch.py`

Cambios:
- Gemini participa exactamente una vez en la etapa de contexto para comprender lenguaje coloquial y hacer una pregunta personalizada.
- No se usa la confirmación mecánica “¿Representa lo que quisiste expresar?”.
- Después de una respuesta de profundización, el chat avanza a frecuencia.
- Si una frase no coincide con el diccionario, pero Gemini la entiende, se crea una propuesta `pending` usando la frase anonimizada, aunque `expresion_nueva` venga vacía.
- Las propuestas siguen requiriendo aprobación humana.
