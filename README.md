# Escucha Laboral V5 académica
Incluye chat, Supabase, guardado anonimizado, Gemini opcional, propuestas de aprendizaje y panel separado de revisión.

## Despliegues
1. Chat público: `app.py`.
2. Panel privado: `review_app.py` como segunda app de Streamlit, protegido por `REVIEW_PASSWORD`.

## Configuración
Ejecutar `supabase/schema.sql` y configurar todos los valores de `.streamlit/secrets.toml.example` en Streamlit Secrets.
