import os
from dotenv import load_dotenv
import pymysql
from pymysql import Error
import pymysql.cursors
import socket
import traceback

# Cargar variables de entorno desde .env si existe
load_dotenv()

def conectar_db():
    try:
        host = os.getenv('DB_HOST', 'localhost')
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        database = os.getenv('DB_NAME', 'db_verifica_bolivia')
        port = int(os.getenv('DB_PORT', '3306'))

        # Verificar que el host/puerto esté accesible antes de intentar conectar
        try:
            sock = socket.create_connection((host, port), timeout=3)
            sock.close()
        except Exception as e:
            msg = f"No se pudo conectar al host {host} en el puerto {port}: {e}"
            print(msg)
            raise ConnectionError(msg)

        conexion = None
        try:
            conexion = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as e:
            print("Error al intentar conectar con pymysql:")
            traceback.print_exc()
            raise
        return conexion
    except Error as e:
        print(f"Error al conectar a MariaDB: {e}")
        print(f"Parametros usados -> host={os.getenv('DB_HOST')}, user={os.getenv('DB_USER')}, database={os.getenv('DB_NAME')}")
        return None

def guardar_verificacion(tipo, datos):
    """
    tipo: 'texto', 'link' o 'imagen'
    datos: Diccionario con las llaves correspondientes a la tabla
    """
    # Validar longitud del título (solo para texto y link)
    if tipo in ['texto', 'link']:
        if len(datos.get('titulo', '')) > 255:
            msg = f"Error: El título excede los 255 caracteres permitidos. Longitud: {len(datos['titulo'])}"
            print(msg)
            raise ValueError(msg)

    # Validar valor de veredicto
    valores_veredicto = ['Falso', 'Verdadero', 'Engañoso', 'No determinado']
    if datos['veredicto'] not in valores_veredicto:
        msg = f"Error: El veredicto '{datos['veredicto']}' no es válido. Valores permitidos: {valores_veredicto}"
        print(msg)
        raise ValueError(msg)

    conn = conectar_db()
    if conn is None:
        msg = "Error: No se pudo establecer conexión con la base de datos."
        print(msg)
        raise ConnectionError(msg)

    cursor = conn.cursor()

    try:
        if tipo == 'texto':
            query = """INSERT INTO verificacion_texto (titulo, contenido, veredicto, confianza) 
                       VALUES (%s, %s, %s, %s)"""
            valores = (datos['titulo'], datos['contenido'], datos['veredicto'], datos['confianza'])
            print(f"Ejecutando query para texto: {query} con valores {valores}")

        elif tipo == 'link':
            query = """INSERT INTO verificacion_link (titulo, url_link, veredicto, confianza) 
                       VALUES (%s, %s, %s, %s)"""
            valores = (datos['titulo'], datos['url_link'], datos['veredicto'], datos['confianza'])
            print(f"Ejecutando query para link: {query} con valores {valores}")

        elif tipo == 'imagen':
            query = """INSERT INTO verificacion_imagen (ruta_img, descripcion, veredicto, confianza) 
                       VALUES (%s, %s, %s, %s)"""
            valores = (datos['ruta_img'], datos['descripcion'], datos['veredicto'], datos['confianza'])
            print(f"Ejecutando query para imagen: {query} con valores {valores}")

        cursor.execute(query, valores)
        conn.commit()
        print("Datos insertados correctamente en la base de datos.")
        return True
    except Error as e:
        # Re-raise to surface the original DB error to the caller
        print(f"Error al insertar datos: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

# FIX #3: Serializar objetos datetime a string ISO para que FastAPI
# pueda convertirlos a JSON sin lanzar un TypeError 500
def serializar_fechas(filas):
    """Convierte objetos datetime en las filas a strings ISO."""
    for fila in filas:
        if isinstance(fila, dict):
            for clave, valor in fila.items():
                if valor and hasattr(valor, 'isoformat'):
                    fila[clave] = valor.isoformat()
    return filas

def obtener_historial():
    conn = conectar_db()
    if conn is None: return {"texto": [], "links": [], "imagenes": []}
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute("SELECT 'texto' as tipo, titulo, veredicto, confianza, fecha FROM verificacion_texto ORDER BY fecha DESC LIMIT 10")
        texto = cursor.fetchall() or []
        
        cursor.execute("SELECT 'link' as tipo, titulo, veredicto, confianza, fecha FROM verificacion_link ORDER BY fecha DESC LIMIT 10")
        links = cursor.fetchall() or []
        
        cursor.execute("SELECT 'imagen' as tipo, ruta_img as titulo, veredicto, confianza, fecha FROM verificacion_imagen ORDER BY fecha DESC LIMIT 10")
        imagenes = cursor.fetchall() or []
        
        return {
            "texto": serializar_fechas(texto),
            "links": serializar_fechas(links),
            "imagenes": serializar_fechas(imagenes)
        }
    except Error as e:
        print(f"Error al obtener historial: {e}")
        return {"texto": [], "links": [], "imagenes": []}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()