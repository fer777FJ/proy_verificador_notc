import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import socket
import traceback

# Cargar variables de entorno
load_dotenv()

def test_connection():
    host = os.getenv('DB_HOST', 'localhost')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    database = os.getenv('DB_NAME', 'db_verifica_bolivia')
    port = int(os.getenv('DB_PORT', 3306))
    
    print(f"Intentando conectar con estos parámetros:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  User: {user}")
    print(f"  Password: {'[configurada]' if password else '[vacía]'}")
    print(f"  Database: {database}")
    print()
    
    # Paso 1: Verificar conectividad TCP al host:puerto
    print("Paso 1: Verificando conectividad TCP...")
    try:
        sock = socket.create_connection((host, port), timeout=3)
        sock.close()
        print(f"✓ Conexión TCP exitosa a {host}:{port}")
    except socket.timeout:
        print(f"✗ Timeout: No se pudo conectar a {host}:{port} en 3 segundos")
        return
    except socket.error as e:
        print(f"✗ Error de conexión TCP: {e}")
        print(f"  - ¿MySQL está corriendo?")
        print(f"  - ¿El puerto {port} está abierto?")
        print(f"  - ¿El host {host} es correcto?")
        return
    
    # Paso 2: Intentar conectar a MySQL
    print("\nPaso 2: Intentando conectar con mysql.connector...")
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        if connection.is_connected():
            print("✓ Conexión exitosa a la base de datos MySQL")
            # Obtener información del servidor
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✓ Versión de MySQL: {version[0]}")
            cursor.close()
            connection.close()
    except Error as e:
        print(f"✗ Error de MySQL: {e}")
        print(f"\nTraceback completo:")
        traceback.print_exc()
        print(f"\nPosibles soluciones:")
        print(f"  1. Verifica que el usuario '{user}' existe en MySQL")
        print(f"  2. Verifica que la contraseña es correcta")
        print(f"  3. Verifica que la base de datos '{database}' existe")
        print(f"  4. Intenta conectar sin especificar base de datos (DB_NAME)")

if __name__ == "__main__":
    test_connection()
