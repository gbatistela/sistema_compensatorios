import streamlit as st
from database import crear_tablas
from services.vencimientos_service import actualizar_vencimientos
from services.usuarios_service import obtener_usuario
from pages.dashboard import mostrar_dashboard
from pages.calendario import mostrar_calendario

crear_tablas()
actualizar_vencimientos()

st.set_page_config(layout="wide")

# ------------------------
# LOGIN
# ------------------------

if "usuario" not in st.session_state:
    st.session_state.usuario = None
    st.session_state.empleado_id = None

if not st.session_state.usuario:

    st.title("Login Sistema RRHH")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):

        user = obtener_usuario(username, password)

        if user:
            st.session_state.usuario = username
            st.session_state.empleado_id = user[1]
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

    st.stop()

# ------------------------
# SISTEMA
# ------------------------

st.title(f"Sistema RRHH - Bienvenido {st.session_state.usuario}")

if st.sidebar.button("Cerrar sesión"):
    st.session_state.usuario = None
    st.session_state.empleado_id = None
    st.rerun()

menu = st.sidebar.selectbox("Sección", [
    "Dashboard",
    "Calendario"
])

if menu == "Dashboard":
    mostrar_dashboard(st.session_state.empleado_id)

elif menu == "Calendario":
    mostrar_calendario(st.session_state.empleado_id)