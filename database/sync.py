import database.db_local as db_local
import database.db_cloud as db_cloud

def sincronizar_registros():
    print("Iniciando proceso de sincronización...")
    
    # 1. Verificar si hay conexión con el servidor MySQL
    if not db_cloud.verificar_conexion_internet():
        print("Sin conexión a internet. El sistema sigue funcionando en modo offline.")
        return False

    # 2. Conectar a ambas bases de datos
    conn_local = db_local.conectar_local()
    cursor_local = conn_local.cursor()
    
    conn_nube = db_cloud.conectar_nube()
    
    if not conn_nube:
        print("Error: No se pudo establecer la sesión con la nube.")
        conn_local.close()
        return False

    cursor_nube = conn_nube.cursor()

    try:
        # 3. Buscar todos los datos de operación diaria que aún no subieron
        cursor_local.execute("SELECT * FROM registros_diarios WHERE sincronizado = 0")
        registros_pendientes = cursor_local.fetchall()

        if not registros_pendientes:
            print("Todos los registros ya están sincronizados al día.")
            return True

        # 4. Preparar la sentencia de inserción para MySQL
        # Nota: Usamos %s para MySQL y evitamos mandar el id_registro local
        # para que MySQL genere su propio ID autoincremental sin conflictos.
        sql_insert = """
            INSERT INTO registros_diarios 
            (id_lote, fecha, mortalidad, alimento_kg, fase, temp_min, temp_max) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        for fila in registros_pendientes:
            valores = (
                fila['id_lote'], 
                fila['fecha'], 
                int(fila['mortalidad']), # Aseguramos formato numérico
                float(fila['alimento_kg']), 
                fila['fase'], 
                float(fila['temp_min']) if fila['temp_min'] else None, 
                float(fila['temp_max']) if fila['temp_max'] else None
            )
            
            # Subir a la nube
            cursor_nube.execute(sql_insert, valores)
            
            # 5. Marcar como sincronizado en la base local usando el ID local
            cursor_local.execute(
                "UPDATE registros_diarios SET sincronizado = 1 WHERE id_registro = ?", 
                (int(fila['id_registro']),)
            )

        # 6. Confirmar la transacción (Commit) en ambas bases
        # Esto es clave: si algo falla en el medio, no se guarda nada a medias.
        conn_nube.commit()
        conn_local.commit()
        
        print(f"¡Éxito! Se sincronizaron {len(registros_pendientes)} registros a la nube.")
        return True

    except Exception as e:
        print(f"Ocurrió un error durante la sincronización: {e}")
        # Rollback: deshacer cualquier cambio si hubo un error (ej. se cortó la luz a la mitad)
        if conn_nube.is_connected():
            conn_nube.rollback()
        conn_local.rollback()
        return False

    finally:
        # 7. Siempre cerrar las conexiones para no dejar puertos abiertos
        conn_local.close()
        if conn_nube.is_connected():
            cursor_nube.close()
            conn_nube.close()

# Bloque de prueba
if __name__ == "__main__":
    sincronizar_registros()