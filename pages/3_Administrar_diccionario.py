import pandas as pd
import streamlit as st

st.set_page_config(page_title="Administrar diccionario", page_icon="📝")
st.title("Administrar diccionario - modo demostración")
st.warning("Este formulario genera una propuesta descargable. No modifica automáticamente el diccionario validado.")

df = pd.read_csv("data/diccionario.csv")
st.dataframe(df, use_container_width=True, hide_index=True)

with st.form("nueva_expresion"):
    expresion = st.text_input("Expresión")
    variantes = st.text_input("Variantes separadas por |")
    dimension = st.selectbox("Dimensión", sorted(df["dimension_probable"].unique().tolist()))
    ambiguedad = st.selectbox("Ambigüedad", ["baja","media","alta"])
    pregunta = st.text_area("Pregunta aclaratoria")
    region = st.text_input("Región", value="Colombia")
    fuente = st.text_input("Fuente o contexto de recolección")
    enviar = st.form_submit_button("Crear propuesta")

if enviar:
    if not expresion.strip() or not pregunta.strip():
        st.error("Expresión y pregunta aclaratoria son obligatorias.")
    else:
        nueva = pd.DataFrame([{
            "id": f"BORRADOR-{len(df)+1:03d}", "expresion": expresion.strip(),
            "variantes": variantes.strip(), "categoria": "pendiente",
            "dimension_probable": dimension, "ambiguedad": ambiguedad,
            "requiere_aclaracion": "si", "pregunta_aclaratoria": pregunta.strip(),
            "region": region.strip(), "estado_validacion": "borrador", "fuente": fuente.strip()
        }])
        st.success("Propuesta creada como borrador. Debe pasar revisión lingüística y psicosocial.")
        st.dataframe(nueva, hide_index=True)
        st.download_button("Descargar propuesta CSV", nueva.to_csv(index=False).encode("utf-8"), "propuesta_expresion.csv", "text/csv")
