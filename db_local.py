import sqlite3
import os

# Nombre del archivo físico de la base de datos local
DB_NAME = "granja_pando_local.db"

def conectar_local():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row 
    return conn

def inicializar_db():
    conn = conectar_local()
    cursor = conn.cursor()

    # 1. Tabla de Dueños
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dueños (
        id_dueño INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        contacto TEXT
    )
    """)

    # 2. Tabla de Granjas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS granjas (
        id_granja INTEGER PRIMARY KEY AUTOINCREMENT,
        id_dueño INTEGER NOT NULL,
        nombre_granja TEXT NOT NULL,
        ubicacion TEXT,
        FOREIGN KEY (id_dueño) REFERENCES dueños(id_dueño) ON DELETE CASCADE
    )
    """)

    # 3. Tabla de Galpones 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS galpones (
        id_galpon INTEGER PRIMARY KEY AUTOINCREMENT,
        id_granja INTEGER NOT NULL,
        numero_galpon TEXT NOT NULL,
        capacidad INTEGER NOT NULL,
        ubicacion_dentro_predio TEXT,
        estado TEXT DEFAULT 'vacio',
        FOREIGN KEY (id_granja) REFERENCES granjas(id_granja) ON DELETE CASCADE
    )
    """)

    # 4. Tabla de Usuarios 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL,
        id_granja INTEGER,
        FOREIGN KEY (id_granja) REFERENCES granjas(id_granja) ON DELETE SET NULL
    )
    """)

    # 5. Tabla de Lotes 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lotes (
        id_lote INTEGER PRIMARY KEY AUTOINCREMENT,
        id_galpon INTEGER NOT NULL,
        fecha_ingreso DATE NOT NULL,
        cantidad_inicial INTEGER NOT NULL,
        estado TEXT DEFAULT 'activo',
        FOREIGN KEY (id_galpon) REFERENCES galpones(id_galpon) ON DELETE CASCADE
    )
    """)

    # 6. Tabla de Mortalidad Diaria 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mortalidad_diaria (
        id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
        id_lote INTEGER NOT NULL,
        fecha DATE NOT NULL,
        mortalidad INTEGER NOT NULL DEFAULT 0,
        sincronizado INTEGER DEFAULT 0,
        FOREIGN KEY (id_lote) REFERENCES lotes(id_lote) ON DELETE CASCADE
    )
    """)

    # 7. Tabla de Ingreso de Alimento 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ingresos_alimento (
        id_ingreso INTEGER PRIMARY KEY AUTOINCREMENT,
        id_granja INTEGER NOT NULL,
        fecha DATE NOT NULL,
        fase TEXT NOT NULL,
        cantidad_recibida_kg REAL NOT NULL,
        remito TEXT,
        sincronizado INTEGER DEFAULT 0,
        FOREIGN KEY (id_granja) REFERENCES granjas(id_granja) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()
    print(f"Base de datos local '{DB_NAME}' actualizada e inicializada correctamente.")


# ==========================================
# FUNCIONES DE CONSULTA Y REGISTRO (Las que faltaban)
# ==========================================

def obtener_granjas():
    conn = conectar_local()
    res = conn.execute("SELECT id_granja, nombre_granja FROM granjas").fetchall()
    conn.close()
    return res

def obtener_galpones_por_granja(id_granja, solo_vacios=False):
    conn = conectar_local()
    sql = "SELECT * FROM galpones WHERE id_granja = ?"
    if solo_vacios:
        sql += " AND estado = 'vacio'"
    res = conn.execute(sql, (id_granja,)).fetchall()
    conn.close()
    return res

def registrar_usuario(username, password, rol, id_granja=None):
    conn = conectar_local()
    try:
        conn.execute("INSERT INTO usuarios (username, password, rol, id_granja) VALUES (?, ?, ?, ?)", 
                     (username, password, rol, id_granja))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al registrar usuario: {e}")
        return False
    finally:
        conn.close()

def registrar_lote(id_galpon, fecha, cantidad):
    conn = conectar_local()
    # 1. Creamos el lote
    conn.execute("INSERT INTO lotes (id_galpon, fecha_ingreso, cantidad_inicial) VALUES (?, ?, ?)", (id_galpon, fecha, cantidad))
    # 2. Marcamos el galpón como ocupado
    conn.execute("UPDATE galpones SET estado = 'activo' WHERE id_galpon = ?", (id_galpon,))
    conn.commit()
    conn.close()

def obtener_lote_activo(id_galpon):
    conn = conectar_local()
    res = conn.execute("SELECT id_lote, cantidad_inicial FROM lotes WHERE id_galpon = ? AND estado = 'activo'", (id_galpon,)).fetchone()
    conn.close()
    return res

def registrar_mortalidad(id_lote, fecha, cantidad):
    conn = conectar_local()
    conn.execute("INSERT INTO mortalidad_diaria (id_lote, fecha, mortalidad) VALUES (?, ?, ?)", (id_lote, fecha, cantidad))
    conn.commit()
    conn.close()

def generar_estadisticas_mortandad(id_galpon):
    conn = conectar_local()
    
    lote = conn.execute("SELECT id_lote, cantidad_inicial FROM lotes WHERE id_galpon = ? AND estado = 'activo'", (id_galpon,)).fetchone()
    if not lote:
        conn.close()
        return None
        
    id_lote = lote['id_lote']
    cantidad_inicial = lote['cantidad_inicial']
    
    res_muertes = conn.execute("SELECT SUM(mortalidad) as total_muertes FROM mortalidad_diaria WHERE id_lote = ?", (id_lote,)).fetchone()
    total_muertes = res_muertes['total_muertes'] if res_muertes['total_muertes'] else 0
    
    detalle = conn.execute("SELECT fecha, mortalidad FROM mortalidad_diaria WHERE id_lote = ? ORDER BY fecha DESC", (id_lote,)).fetchall()
    conn.close()
    
    porcentaje = (total_muertes / cantidad_inicial) * 100 if cantidad_inicial > 0 else 0
    
    return {
        "cantidad_inicial": cantidad_inicial,
        "total_muertes": total_muertes,
        "porcentaje_mortandad": round(porcentaje, 2),
        "detalle_diario": detalle
    }
    
def obtener_dueños():
    conn = conectar_local()
    res = conn.execute("SELECT id_dueño, nombre || ' ' || apellido AS nombre_completo FROM dueños").fetchall()
    conn.close()
    return res

def registrar_dueño(nombre, apellido, contacto):
    conn = conectar_local()
    conn.execute("INSERT INTO dueños (nombre, apellido, contacto) VALUES (?, ?, ?)", (nombre, apellido, contacto))
    conn.commit()
    conn.close()

def registrar_granja(id_dueño, nombre, ubicacion):
    conn = conectar_local()
    conn.execute("INSERT INTO granjas (id_dueño, nombre_granja, ubicacion) VALUES (?, ?, ?)", (id_dueño, nombre, ubicacion))
    conn.commit()
    conn.close()

def registrar_galpon(id_granja, numero, capacidad):
    conn = conectar_local()
    # Registramos el galpón, por defecto la base de datos ya le pone estado = 'vacio'
    conn.execute("INSERT INTO galpones (id_granja, numero_galpon, capacidad) VALUES (?, ?, ?)", (id_granja, numero, capacidad))
    conn.commit()
    conn.close()
    
def registrar_ingreso_alimento(id_granja, fecha, fase, cantidad_kg, remito):
    conn = conectar_local()
    try:
        conn.execute("""
            INSERT INTO ingresos_alimento (id_granja, fecha, fase, cantidad_recibida_kg, remito)
            VALUES (?, ?, ?, ?, ?)
        """, (id_granja, fecha, fase, cantidad_kg, remito))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al registrar alimento: {e}")
        return False
    finally:
        conn.close()
        
def obtener_reporte_alimento(id_granja, fase):
    """
    Obtiene los registros de alimento para una granja y fase específica.
    """
    conn = conectar_local()
    # Traemos el detalle para la tabla
    registros = conn.execute("""
        SELECT fecha, cantidad_recibida_kg, remito 
        FROM ingresos_alimento 
        WHERE id_granja = ? AND fase = ? 
        ORDER BY fecha DESC
    """, (id_granja, fase)).fetchall()
    
    # Calculamos el total acumulado para el resumen
    total = conn.execute("""
        SELECT SUM(cantidad_recibida_kg) as total 
        FROM ingresos_alimento 
        WHERE id_granja = ? AND fase = ?
    """, (id_granja, fase)).fetchone()
    
    conn.close()
    return {
        "detalle": registros,
        "total_acumulado": total['total'] if total['total'] else 0
    }
    
def obtener_proyeccion_alimento(id_granja, fase):
    """
    Calcula cuántos kilos faltan enviar basándose en la población total activa.
    """
    # Tabla técnica de consumo (Kilos totales por pollo para completar cada fase)
    # Ejemplo: En F1 un pollo consume 0.45kg en total. Ajustá estos valores según tu tabla.
    ESTANDARES_CONSUMO = {
        "F1": 0.25, 
        "F2": 0.85,
        "F3": 1.0,
        "F4": 1.5,
        "F5": 2.0
    }
    
    consumo_por_ave = ESTANDARES_CONSUMO.get(fase, 0)
    conn = conectar_local()
    
    # 1. Sumar población inicial de todos los lotes activos en la granja
    poblacion_total = conn.execute("""
        SELECT SUM(l.cantidad_inicial) as total_aves
        FROM lotes l
        JOIN galpones g ON l.id_galpon = g.id_galpon
        WHERE g.id_granja = ? AND l.estado = 'activo'
    """, (id_granja,)).fetchone()['total_aves']
    
    poblacion_total = poblacion_total if poblacion_total else 0
    
    # 2. Calcular requerimiento teórico total para esa población
    kilos_requeridos = poblacion_total * consumo_por_ave
    
    # 3. Sumar lo que ya se recibió en la granja para esa fase
    kilos_recibidos = conn.execute("""
        SELECT SUM(cantidad_recibida_kg) as total_recibido
        FROM ingresos_alimento
        WHERE id_granja = ? AND fase = ?
    """, (id_granja, fase)).fetchone()['total_recibido']
    
    kilos_recibidos = kilos_recibidos if kilos_recibidos else 0
    conn.close()
    
    faltante = kilos_requeridos - kilos_recibidos
    
    return {
        "poblacion_total": poblacion_total,
        "kilos_requeridos": round(kilos_requeridos, 2),
        "kilos_recibidos": round(kilos_recibidos, 2),
        "kilos_faltantes": round(max(0, faltante), 2) # No mostramos negativos
    }

if __name__ == "__main__":
    inicializar_db()