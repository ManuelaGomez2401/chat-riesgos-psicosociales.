# Escucha Laboral - Versión 2

MVP universitario conversacional para la identificación preventiva de señales asociadas con factores de riesgo psicosocial en entornos laborales colombianos.

## Novedades de la versión 2
- Historial de conversación con `st.session_state`.
- Interfaz de chat con `st.chat_message` y `st.chat_input`.
- Pregunta aclaratoria.
- Frecuencia, duración e impacto.
- Orientación preventiva experimental.
- Botón para reiniciar.
- Código separado en módulos.

## Ejecutar localmente

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Instalar y ejecutar:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Ejecutar pruebas

```bash
pytest
```

## Publicar en Streamlit Community Cloud
- Repositorio: el repositorio de GitHub donde se suban estos archivos.
- Rama: `main`.
- Archivo principal: `app.py`.

## Advertencia
Este prototipo no diagnostica, no reemplaza la Batería de Riesgo Psicosocial y debe probarse inicialmente con datos ficticios o anonimizados.
