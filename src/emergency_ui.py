import streamlit as st

def mostrar_botones_emergencia():
    st.markdown('''<style>.call-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0}.call-btn{display:block;text-align:center;text-decoration:none!important;padding:14px;border-radius:14px;font-weight:700}.call-106{background:#527A61;color:white!important}.call-123{background:#B42318;color:white!important}@media(max-width:600px){.call-grid{grid-template-columns:1fr}}</style><div class="call-grid"><a class="call-btn call-106" href="tel:106">📞 Abrir llamada a Línea 106</a><a class="call-btn call-123" href="tel:123">🚑 Abrir llamada a emergencias 123</a></div>''',unsafe_allow_html=True)
    st.caption('El botón abre el marcador del teléfono; la llamada no se realiza automáticamente.')
