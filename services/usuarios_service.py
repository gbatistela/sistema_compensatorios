from database import conectar

def obtener_usuario(username, password):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, empleado_id
        FROM usuarios
        WHERE username=? AND password=?
    """, (username, password))

    user = cursor.fetchone()
    conn.close()
    return user