import streamlit as st
import plotly.express as px
from services.eventos_service import obtener_eventos

def mostrar_dashboard():
    st.subheader("📊 Dashboard")

    df = obtener_eventos()

    if df.empty:
        st.info("Sin datos.")
        return

    resumen = df.groupby(["nombre", "estado"])["cantidad"].sum().reset_index()

    st.dataframe(resumen)

    fig = px.bar(
        resumen,
        x="nombre",
        y="cantidad",
        color="estado",
        title="Resumen general"
    )

    st.plotly_chart(fig, use_container_width=True)
