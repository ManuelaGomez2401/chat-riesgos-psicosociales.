# Escucha Laboral V4

Aplicación única con avatar de perrito blanco y negro, animación CSS, diseño salvia, Gemini opcional y almacenamiento opcional en Supabase.

## Modo demostración
Funciona sin claves. No guarda chats ni llama a Gemini.

## Activar Gemini
Agrega `GEMINI_API_KEY` en Streamlit Secrets. La IA solo se consulta cuando las reglas no comprenden y la persona autoriza ese uso.

## Activar guardado
1. Crea un proyecto Supabase.
2. Ejecuta `supabase/schema.sql`.
3. Agrega `SUPABASE_URL` y `SUPABASE_KEY` en Streamlit Secrets.
4. El guardado solo ocurre cuando la persona autoriza guardar la conversación.

## GitHub
Elimina cualquier carpeta antigua `pages/`. Sube el contenido interno de esta carpeta. Archivo principal: `app.py`.
