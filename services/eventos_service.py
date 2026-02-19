import pandas as pd
from datetime import timedelta
from database import conectar

def obtener_eventos():
    conn = conectar()
    df = pd.read_sql_query("""
        SELECT e.*, emp.nombre
        FROM eventos e
        LEFT JOIN empleados emp ON e.empleado_id = emp.id
    """, conn)
    conn.close()
    return df

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
                cursor.execute(
                    "UPDATE eventos SET estado='compensado' WHERE id=?",
                    (sabado_id,)
                )
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
