import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import plotly.express as px

DB_NAME = "compensatorios.db"


# =========================
# DB
# =========================
def conectar():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS empleados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE,
        activo INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empleado_id INTEGER,
        fecha TEXT,
        cantidad REAL,
        estado TEXT,
        tipo TEXT,
        fecha_vencimiento TEXT
    )
    """)

    conn.commit()
    conn.close()


def obtener_empleados():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM empleados WHERE activo=1", conn)
    conn.close()
    return df


def obtener_eventos():
    conn = conectar()
    df = pd.read_sql_query("""
    SELECT e.*, emp.nombre
    FROM eventos e
    LEFT JOIN empleados emp ON e.empleado_id = emp.id
    """, conn)
    conn.close()
    return df

def actualizar_vencimientos():

    conn = conectar()
    cursor = conn.cursor()

    hoy = datetime.today().strftime("%Y-%m-%d")

    cursor.execute("""
    UPDATE eventos
    SET estado='vencido'
    WHERE tipo='sabado'
    AND estado='disponible'
    AND fecha_vencimiento < ?
    """, (hoy,))

    conn.commit()
    conn.close()



# =========================
# EMPLEADOS
# =========================
def agregar_empleado(nombre):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO empleados (nombre) VALUES (?)", (nombre,))
    conn.commit()
    conn.close()


# =========================
# EVENTOS
# =========================
def agregar_evento(empleado_id, fecha, tipo, cantidad):

    conn = conectar()
    cursor = conn.cursor()

    if tipo == "sabado":

        fecha_venc = fecha + timedelta(days=45)

        cursor.execute("""
        INSERT INTO eventos
        (empleado_id, fecha, cantidad, estado, tipo, fecha_vencimiento)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            empleado_id,
            fecha.strftime("%Y-%m-%d"),
            cantidad,
            "disponible",
            "sabado",
            fecha_venc.strftime("%Y-%m-%d")
        ))

    elif tipo == "descanso":

        # Registrar descanso
        cursor.execute("""
        INSERT INTO eventos
        (empleado_id, fecha, cantidad, estado, tipo, fecha_vencimiento)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            empleado_id,
            fecha.strftime("%Y-%m-%d"),
            cantidad,
            "usado",
            "descanso",
            fecha.strftime("%Y-%m-%d")
        ))

        # Buscar sábados disponibles (FIFO)
        cursor.execute("""
        SELECT id, cantidad FROM eventos
        WHERE empleado_id=?
        AND tipo='sabado'
        AND estado='disponible'
        ORDER BY fecha ASC
        """, (empleado_id,))

        sabados = cursor.fetchall()

        restante = cantidad

        for sabado_id, sabado_cant in sabados:

            if restante <= 0:
                break

            if sabado_cant <= restante:
                cursor.execute("""
                UPDATE eventos
                SET estado='compensado'
                WHERE id=?
                """, (sabado_id,))
                restante -= sabado_cant
            else:
                nueva_cant = sabado_cant - restante
                cursor.execute("""
                UPDATE eventos
                SET cantidad=?, estado='disponible'
                WHERE id=?
                """, (nueva_cant, sabado_id))
                restante = 0

    conn.commit()
    conn.close()



def borrar_evento(event_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM eventos WHERE id=?", (event_id,))
    conn.commit()
    conn.close()


def actualizar_evento(event_id, fecha, tipo, cantidad):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE eventos
    SET fecha=?, tipo=?, cantidad=?
    WHERE id=?
    """, (
        fecha.strftime("%Y-%m-%d"),
        tipo,
        cantidad,
        event_id
    ))
    conn.commit()
    conn.close()


# =========================
# APP
# =========================
crear_tablas()
st.set_page_config(layout="wide")
st.title("Sistema RRHH - Compensatorios On City Aristobulo")

menu = st.sidebar.selectbox("Sección", [
    "Dashboard",
    "Empleados",
    "Calendario"
])

# 🔥 Actualiza vencimientos automáticamente al cargar la app
actualizar_vencimientos()

df_eventos = obtener_eventos()
df_empleados = obtener_empleados()



# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":

    if df_eventos.empty:
        st.info("Sin datos.")
    else:
        resumen = df_eventos.groupby(["nombre", "estado"])["cantidad"].sum().reset_index()
        st.dataframe(resumen)

        fig = px.bar(resumen, x="nombre", y="cantidad", color="estado",
                     title="Resumen general")
        st.plotly_chart(fig, use_container_width=True)


# =========================
# EMPLEADOS
# =========================
elif menu == "Empleados":

    st.subheader("Alta empleado")

    nuevo = st.text_input("Nombre empleado")

    if st.button("Agregar"):
        agregar_empleado(nuevo)
        st.success("Empleado agregado")
        st.rerun()

    st.subheader("Lista empleados")
    st.dataframe(df_empleados)


# =========================
# CALENDARIO PRO
# =========================
elif menu == "Calendario":

    st.subheader("📅 Calendario General")

    # =========================
    # ARMAR EVENTOS
    # =========================
    eventos = []

    for _, row in df_eventos.iterrows():

        estado = row["estado"]
        tipo = row["tipo"]

        if tipo == "descanso":
            color = "#bb8fce"
        elif estado == "disponible":
            color = "#a9dfbf"
        elif estado == "compensado":
            color = "#5dade2"
        elif estado == "vencido":
            color = "#e74c3c"
        else:
            color = "#95a5a6"

        eventos.append({
            "id": str(row["id"]),
            "title": f"{row['nombre']} ({tipo})",
            "start": row["fecha"],
            "color": color
        })

    calendar_options = {
        "initialView": "dayGridMonth",
        "selectable": True
    }

    selected = calendar(events=eventos, options=calendar_options)

    # ==================================================
    # POPUP CREAR
    # ==================================================
    @st.dialog("Agregar evento")
    def popup_agregar(fecha_dt):

        if df_empleados.empty:
            st.warning("No hay empleados cargados.")
            return

        empleado = st.selectbox("Empleado", df_empleados["nombre"])
        empleado_id = df_empleados[df_empleados["nombre"] == empleado]["id"].values[0]

        tipo = st.selectbox("Tipo", ["sabado", "descanso"])
        cantidad = st.selectbox("Cantidad", [0.5, 1.0])

        if st.button("Guardar"):
            agregar_evento(empleado_id, fecha_dt, tipo, cantidad)
            st.success("Evento agregado")
            st.rerun()

    # ==================================================
    # POPUP EDITAR
    # ==================================================
    @st.dialog("Editar evento")
    def popup_editar(event_id):

        evento = df_eventos[df_eventos["id"] == event_id].iloc[0]
        fecha_original = datetime.strptime(evento["fecha"], "%Y-%m-%d")

        st.write(f"Empleado: **{evento['nombre']}**")

        nueva_fecha = st.date_input("Fecha", fecha_original)

        nuevo_tipo = st.selectbox(
            "Tipo",
            ["sabado", "descanso"],
            index=0 if evento["tipo"] == "sabado" else 1
        )

        nueva_cantidad = st.selectbox(
            "Cantidad",
            [0.5, 1.0],
            index=0 if evento["cantidad"] == 0.5 else 1
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Actualizar"):
                actualizar_evento(event_id, nueva_fecha, nuevo_tipo, nueva_cantidad)
                st.success("Actualizado")
                st.rerun()

        with col2:
            if st.button("Borrar"):
                borrar_evento(event_id)
                st.warning("Eliminado")
                st.rerun()

    # ==================================================
    # DETECTAR CLICKS
    # ==================================================
    if selected:

        if "dateClick" in selected:
            fecha_click = selected["dateClick"]["date"][:10]
            fecha_dt = datetime.strptime(fecha_click, "%Y-%m-%d")
            popup_agregar(fecha_dt)

        if "eventClick" in selected:
            event_id = int(selected["eventClick"]["event"]["id"])
            popup_editar(event_id)
