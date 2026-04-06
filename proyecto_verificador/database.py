import mysql.connector
from mysql.connector import Error

def conectar_db():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',      # Cambia si tienes otro usuario
            password='',      # Pon tu contraseña de MariaDB
            database='db_verifica_bolivia'
        )
        return conexion
    except Error as e:
        print(f"Error al conectar a MariaDB: {e}")
        return None

def guardar_verificacion(tipo, datos):
    """
    tipo: 'texto', 'link' o 'imagen'
    datos: Diccionario con las llaves correspondientes a la tabla
    """
    conn = conectar_db()
    if conn is None: return False
    
    cursor = conn.cursor()
    
    try:
        if tipo == 'texto':
            query = """INSERT INTO verificacion_texto (titulo, contenido, veredicto, confianza) 
                       VALUES (%s, %s, %s, %s)"""
            valores = (datos['titulo'], datos['contenido'], datos['veredicto'], datos['confianza'])
            
        elif tipo == 'link':
            query = """INSERT INTO verificacion_link (titulo, url_link, veredicto, confianza) 
                       VALUES (%s, %s, %s, %s)"""
            valores = (datos['titulo'], datos['url_link'], datos['veredicto'], datos['confianza'])
            
        elif tipo == 'imagen':
            query = """INSERT INTO verificacion_imagen (ruta_img, descripcion, veredicto, confianza) 
                       VALUES (%s, %s, %s, %s)"""
            valores = (datos['ruta_img'], datos['descripcion'], datos['veredicto'], datos['confianza'])

        cursor.execute(query, valores)
        conn.commit()
        return True
    except Error as e:
        print(f"Error al insertar datos: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
        
        
def obtener_historial():
    conn = conectar_db()
    if conn is None: return []
    cursor = conn.cursor(dictionary=True) # dictionary=True para que devuelva JSON-friendly
    
    try:
        # Consultamos las 10 últimas de cada tabla
        cursor.execute("SELECT 'texto' as tipo, titulo, veredicto, confianza, fecha FROM verificacion_texto ORDER BY fecha DESC LIMIT 10")
        texto = cursor.fetchall()
        
        cursor.execute("SELECT 'link' as tipo, titulo, veredicto, confianza, fecha FROM verificacion_link ORDER BY fecha DESC LIMIT 10")
        links = cursor.fetchall()
        
        cursor.execute("SELECT 'imagen' as tipo, ruta_img as titulo, veredicto, confianza, fecha FROM verificacion_imagen ORDER BY fecha DESC LIMIT 10")
        imagenes = cursor.fetchall()
        
        # Unimos todo en una sola lista o lo mandamos separado
        return {"texto": texto, "links": links, "imagenes": imagenes}
    finally:
        cursor.close()
        conn.close()