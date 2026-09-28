import streamlit as st
import pandas as pd
import unicodedata

st.set_page_config(page_title='Escucha Laboral', page_icon='💬')

@st.cache_data
def cargar_diccionario():
    return pd.read_csv('data/diccionario.csv')

def normalizar(texto):
    texto = unicodedata.normalize('NFD', str(texto).lower().strip())
    return ''.join(c for c in texto if unicodedata.category(c) != 'Mn')

def encontrar(mensaje, df):
    msg = normalizar(mensaje)
    for _, fila in df.iterrows():
        expresiones = [fila['expresion']]
        if pd.notna(fila['variantes']):
            expresiones += str(fila['variantes']).split('|')
        if any(normalizar(x) in msg for x in expresiones):
            return fila
    return None

st.title('Escucha Laboral')
st.caption('MVP académico de orientación preventiva')
st.warning('Este prototipo no diagnostica, no reemplaza la Batería de Riesgo Psicosocial ni sustituye la atención profesional.')

acepta = st.checkbox('Comprendo el propósito y acepto participar voluntariamente en esta demostración.')
if acepta:
    mensaje = st.text_area('Cuéntame cómo te has sentido con tu trabajo durante las últimas semanas.')
    if st.button('Continuar') and mensaje:
        fila = encontrar(mensaje, cargar_diccionario())
        if fila is not None:
            st.info('Gracias por compartirlo. Antes de sacar conclusiones, quisiera comprender mejor la situación.')
            st.write(fila['pregunta_aclaratoria'])
            st.caption('Dimensión provisional: ' + str(fila['dimension_probable']))
        else:
            st.info('Gracias por contarlo. ¿Qué situación del trabajo es la que más está influyendo en cómo te sientes?')
