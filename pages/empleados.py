import streamlit as st
from services.empleados_service import obtener_empleados, agregar_empleado

def mostrar_empleados():
    st.subheader("👥 Empleados")

    nuevo = st.text_input("Nombre empleado")

    if st.button("Agregar"):
        agregar_empleado(nuevo)
        st.success("Empleado agregado")
        st.rerun()

    df = obtener_empleados()
    st.dataframe(df)
