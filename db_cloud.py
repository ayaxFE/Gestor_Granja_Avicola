import mysql.connector
from config import DB_CONFIG

def conectar_nube():
    """
    Establece la conexión con la base de datos MySQL central.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error de conexión a la nube: {err}")
        return None

def verificar_conexion_internet():
    """
    Prueba rápida para saber si hay conexión antes de intentar sincronizar.
    Retorna True si hay conexión, False si la granja está offline.
    """
    conn = conectar_nube()
    if conn and conn.is_connected():
        conn.close()
        return True
    return False

# --- FUNCIONES PARA EL SUPERVISOR (Ejecutan directo en la nube) ---

def obtener_reporte_global_mortalidad():
    """
    Extrae los datos consolidados de todas las granjas.
    """
    conn = conectar_nube()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT g.nombre_granja, l.nro_galpon, r.fecha, r.mortalidad
            FROM registros_diarios r
            JOIN lotes l ON r.id_lote = l.id_lote
            JOIN granjas g ON l.id_granja = g.id_granja
            ORDER BY r.fecha DESC
        """
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        if conn.is_connected():
            conn.close()