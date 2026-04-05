import sqlite3

conn = sqlite3.connect("bewerbungen.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS bewerbungen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firma TEXT,
    stelle TEXT,
    status TEXT,
    notizen TEXT
)
""")

conn.commit()
conn.close()

print("Datenbank erstellt!")