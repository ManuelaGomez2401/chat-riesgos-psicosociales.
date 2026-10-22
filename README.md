# Escucha Laboral V4.2

Restablece las autorizaciones separadas, Gemini opcional y guardado opcional en Supabase, conservando el protocolo prioritario y los avatares de perrito y persona.

## Secrets
```toml
GEMINI_API_KEY="..."
SUPABASE_URL="..."
SUPABASE_KEY="..."
```

Si una integración no está configurada, su autorización aparece deshabilitada con una explicación.

## Seguridad
Cada mensaje pasa primero por `src/safety.py`. Gemini no interviene en el protocolo prioritario.
