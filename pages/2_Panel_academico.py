import pandas as pd
import plotly.express as px
import streamlit as st
from src.storage import obtener_resultados, supabase_configurado

st.set_page_config(page_title="Panel académico", page_icon="📊", layout="wide")
st.title("Panel académico V3")

if supabase_configurado():
    datos = pd.DataFrame(obtener_resultados())
else:
    st.info("Modo demostración: el panel usa casos ficticios incluidos en data/resultados_demo.csv.")
    datos = pd.read_csv("data/resultados_demo.csv")

if datos.empty:
    st.warning("Aún no hay resultados para mostrar."); st.stop()

c1,c2,c3,c4 = st.columns(4)
c1.metric("Sesiones", len(datos))
c2.metric("Utilidad promedio", round(datos["utilidad"].mean(), 2))
c3.metric("Claridad promedio", round(datos["claridad"].mean(), 2))
c4.metric("Comprensión positiva", f"{round((datos['comprension']=='Sí').mean()*100,1)}%")

st.caption("No se muestran segmentaciones con menos de 5 registros.")
if len(datos) >= 5:
    fig = px.histogram(datos, x="orientacion", title="Distribución de orientaciones")
    st.plotly_chart(fig, use_container_width=True)
    fig2 = px.histogram(datos, x="frecuencia", title="Frecuencia reportada")
    st.plotly_chart(fig2, use_container_width=True)

st.dataframe(datos[["codigo_anonimo","orientacion","comprension","utilidad","claridad"]], use_container_width=True, hide_index=True)
