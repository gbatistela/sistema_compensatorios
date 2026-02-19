from datetime import datetime
from database import conectar

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
