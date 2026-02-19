import streamlit as st
from datetime import datetime
from streamlit_calendar import calendar
from services.eventos_service import obtener_eventos, agregar_evento, borrar_evento
from services.empleados_service import obtener_empleados

import logging

logger = logging.getLogger("CALENDARIO")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


def mostrar_calendario():
    st.subheader("📅 Calendario General")

    logger.info("---- Cargando calendario ----")

    df_eventos = obtener_eventos()
    df_empleados = obtener_empleados()

    logger.info(f"Eventos encontrados: {len(df_eventos)}")
    logger.info(f"Empleados encontrados: {len(df_empleados)}")

    eventos = []

    for _, row in df_eventos.iterrows():

        logger.info(f"Procesando evento ID={row['id']} | empleado={row['nombre']} | tipo={row['tipo']}")

        if row["tipo"] == "descanso":
            color = "#bb8fce"
        elif row["estado"] == "disponible":
            color = "#a9dfbf"
        elif row["estado"] == "compensado":
            color = "#5dade2"
        elif row["estado"] == "vencido":
            color = "#e74c3c"
        else:
            color = "#95a5a6"

        # Detectar nombre None
        nombre = row["nombre"]
        if nombre is None:
            logger.error(f"⚠ Evento ID={row['id']} tiene nombre NULL")

        eventos.append({
            "id": str(row["id"]),
            "title": f"{nombre} ({row['tipo']})",
            "start": row["fecha"],
            "color": color
        })

    selected = calendar(events=eventos, options={
        "initialView": "dayGridMonth",
        "selectable": True
    })

    logger.info(f"Selected devuelto por calendar: {selected}")

    @st.dialog("Agregar evento")
    def popup_agregar(fecha_dt):

        logger.info(f"Abrir popup para fecha {fecha_dt}")

        empleado = st.selectbox("Empleado", df_empleados["nombre"])
        empleado_id = int(df_empleados[df_empleados["nombre"] == empleado]["id"].values[0])


        tipo = st.selectbox("Tipo", ["sabado", "descanso"])
        cantidad = st.selectbox("Cantidad", [0.5, 1.0])

        if st.button("Guardar"):
            logger.info(f"Guardando evento | empleado_id={empleado_id} | tipo={tipo} | cantidad={cantidad}")
            agregar_evento(empleado_id, fecha_dt, tipo, cantidad)
            logger.info("Evento guardado correctamente")
            st.success("Evento agregado")
            st.rerun()

    if selected and "dateClick" in selected:
        fecha_click = selected["dateClick"]["date"][:10]
        logger.info(f"Click en fecha: {fecha_click}")
        fecha_dt = datetime.strptime(fecha_click, "%Y-%m-%d")
        popup_agregar(fecha_dt)
