import streamlit as st
from database import crear_tablas
from services.vencimientos_service import actualizar_vencimientos
from pages.dashboard import mostrar_dashboard
from pages.empleados import mostrar_empleados
from pages.calendario import mostrar_calendario



crear_tablas()
actualizar_vencimientos()

st.set_page_config(layout="wide")
st.title("Sistema RRHH - Compensatorios")

menu = st.sidebar.selectbox("Sección", [
    "Dashboard",
    "Empleados",
    "Calendario"
])

if menu == "Dashboard":
    mostrar_dashboard()

elif menu == "Empleados":
    mostrar_empleados()

elif menu == "Calendario":
    mostrar_calendario()
