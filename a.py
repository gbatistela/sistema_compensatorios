import sqlite3

conn = sqlite3.connect("compensatorios.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM eventos")
conn.commit()
conn.close()

print("Eventos limpiados")
