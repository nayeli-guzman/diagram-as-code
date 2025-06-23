from eralchemy import render_er
import sqlite3
import os

def test_entidad_relacion_sqlite():
    # Crea una base de datos SQLite de ejemplo con varias tablas y relaciones
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    # Tabla de usuarios
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name VARCHAR,
        email VARCHAR
    )''')
    # Tabla de posts
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        title VARCHAR,
        content TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    # Tabla de comentarios
    cursor.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY,
        post_id INTEGER,
        user_id INTEGER,
        comment TEXT,
        FOREIGN KEY(post_id) REFERENCES posts(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

    # Genera el diagrama
    output_path = 'diagrama_er.png'
    render_er('sqlite:///test.db', output_path)
    if os.path.exists(output_path):
        print(f"¡Diagrama generado como {output_path}!")
    else:
        print("No se generó el diagrama.")

if __name__ == "__main__":
    test_entidad_relacion_sqlite()
