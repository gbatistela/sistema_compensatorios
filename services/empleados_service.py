import pandas as pd
from database import conectar

def obtener_empleados():
    conn = conectar()
    df = pd.read_sql_query(
        "SELECT * FROM empleados WHERE activo=1",
        conn
    )
    conn.close()
    return df

def agregar_empleado(nombre):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO empleados (nombre) VALUES (?)",
        (nombre,)
    )
    conn.commit()
    conn.close()
