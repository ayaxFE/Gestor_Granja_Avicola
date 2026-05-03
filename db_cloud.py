import sqlite3
import os

# Obtenemos la ruta absoluta de la carpeta donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "granja_pando_local.db")

def conectar_local():
    """Establece conexión con SQLite asegurando que la ruta sea válida."""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row 
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con SQLite: {e}")
        return None

def inicializar_db():
    """Crea todas las tablas siguiendo la lógica de la clienta."""
    conn = conectar_local()
    if not conn: return
    
    cursor = conn.cursor()

    # 1. Tabla de Dueños
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dueños (
        id_dueño INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        contacto TEXT
    )""")

    # 2. Tabla de Granjas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS granjas (
        id_granja INTEGER PRIMARY KEY AUTOINCREMENT,
        id_dueño INTEGER NOT NULL,
        nombre_granja TEXT NOT NULL,
        ubicacion TEXT,
        FOREIGN KEY (id_dueño) REFERENCES dueños(id_dueño) ON DELETE CASCADE
    )""")

    # 3. Tabla de Galpones 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS galpones (
        id_galpon INTEGER PRIMARY KEY AUTOINCREMENT,
        id_granja INTEGER NOT NULL,
        numero_galpon TEXT NOT NULL,
        capacidad INTEGER NOT NULL,
        estado TEXT DEFAULT 'vacio',
        FOREIGN KEY (id_granja) REFERENCES granjas(id_granja) ON DELETE CASCADE
    )""")

    # 4. Tabla de Usuarios 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL,
        id_granja INTEGER,
        FOREIGN KEY (id_granja) REFERENCES granjas(id_granja) ON DELETE SET NULL
    )""")

    # 5. Tabla de Lotes 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lotes (
        id_lote INTEGER PRIMARY KEY AUTOINCREMENT,
        id_galpon INTEGER NOT NULL,
        fecha_ingreso DATE NOT NULL,
        cantidad_inicial INTEGER NOT NULL,
        estado TEXT DEFAULT 'activo',
        FOREIGN KEY (id_galpon) REFERENCES galpones(id_galpon) ON DELETE CASCADE
    )""")

    # 6. Tabla de Mortalidad Diaria 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mortalidad_diaria (
        id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
        id_lote INTEGER NOT NULL,
        fecha DATE NOT NULL,
        mortalidad INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (id_lote) REFERENCES lotes(id_lote) ON DELETE CASCADE
    )""")

    conn.commit()
    conn.close()
    print(f"Base de datos inicializada en: {DB_NAME}")

# Funciones auxiliares para que el sistema funcione
def obtener_granjas():
    conn = conectar_local()
    res = conn.execute("SELECT id_granja, nombre_granja FROM granjas").fetchall()
    conn.close()
    return res

def registrar_usuario(u, p, r, id_g=None):
    conn = conectar_local()
    try:
        conn.execute("INSERT INTO usuarios (username, password, rol, id_granja) VALUES (?, ?, ?, ?)", (u, p, r, id_g))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

if __name__ == "__main__":
    inicializar_db()