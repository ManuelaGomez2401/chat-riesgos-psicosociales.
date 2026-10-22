# Escucha Laboral V3

MVP universitario para validación de un chat preventivo sobre factores de riesgo psicosocial.

## Funciones
- Coincidencia exacta y aproximada con RapidFuzz.
- Varias dimensiones en un mensaje.
- Negación básica.
- Conversación multietapa.
- Retroalimentación final.
- Panel académico agregado.
- Administrador de expresiones en modo borrador.
- Supabase opcional. Sin credenciales funciona en modo demostración.

## Ejecutar
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Probar
```bash
pytest
```

## Supabase opcional
1. Crear un proyecto en Supabase.
2. Ejecutar `supabase/schema.sql` en SQL Editor.
3. Copiar `.streamlit/secrets.toml.example` como `.streamlit/secrets.toml`.
4. Completar URL y anon key.
5. Nunca subir `secrets.toml` a GitHub.

## Streamlit Community Cloud
Rama: `main`. Archivo principal: `app.py`. Configurar secretos desde Advanced settings si se activa Supabase.
