from database import conectar

conn = conectar()
cursor = conn.cursor()

usuarios = [
    ("gbatistela", "1234", 1),
    ("flor.v", "1234", 2),
    ("mati.m", "1234", 3),
    ("maxi.p", "1234", 4),
]

cursor.executemany(
    "INSERT OR IGNORE INTO usuarios (username, password, empleado_id) VALUES (?, ?, ?)",
    usuarios
)

conn.commit()
conn.close()