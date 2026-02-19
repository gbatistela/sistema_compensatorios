import sqlite3
from config import DB_NAME

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
