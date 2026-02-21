import streamlit as st
import plotly.express as px
from services.eventos_service import obtener_eventos

def mostrar_dashboard(empleado_id):
    st.subheader("📊 Mi Dashboard")

    df = obtener_eventos()

    df = df[df["empleado_id"] == empleado_id]

    if df.empty:
        st.info("Sin datos.")
        return

    resumen = df.groupby(["estado"])["cantidad"].sum().reset_index()

    st.dataframe(resumen)

    fig = px.bar(
        resumen,
        x="estado",
        y="cantidad",
        title="Resumen personal"
    )

    st.plotly_chart(fig, use_container_width=True)