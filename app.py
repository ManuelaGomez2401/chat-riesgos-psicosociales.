import streamlit as st

st.set_page_config(page_title="Escucha Laboral V3", page_icon="💬", layout="wide")

st.title("Escucha Laboral V3")
st.subheader("MVP de investigación y validación")
st.write(
    "Esta versión mejora la detección lingüística, reconoce varias dimensiones, "
    "recoge retroalimentación y agrega un panel académico."
)
st.warning(
    "Prototipo académico: no diagnostica, no sustituye la Batería de Riesgo "
    "Psicosocial ni reemplaza la atención profesional. Usa datos ficticios o anonimizados."
)

col1, col2, col3 = st.columns(3)
with col1:
    st.info("**1. Chat preventivo**\n\nConversación multietapa con coincidencia exacta y aproximada.")
with col2:
    st.info("**2. Panel académico**\n\nMétricas agregadas de los casos de demostración.")
with col3:
    st.info("**3. Administrar diccionario**\n\nFormulario para preparar nuevas expresiones sin cambiar código.")

st.markdown("### Cómo comenzar")
st.markdown(
    "Usa el menú lateral para abrir **Chat preventivo**. La página de administración "
    "trabaja en modo demostración y genera archivos descargables; no modifica producción."
)
