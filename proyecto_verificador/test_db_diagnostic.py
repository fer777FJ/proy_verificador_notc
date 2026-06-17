import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import socket
import traceback

# Cargar variables de entorno
load_dotenv()

def test_connection_without_db():
    """Intenta conectar SIN especificar base de datos (para verificar credenciales)"""
    host = os.getenv('DB_HOST', 'localhost')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    port = int(os.getenv('DB_PORT', 3306))
    
    print("\n" + "="*60)
    print("TEST 1: Conectar SIN especificar base de datos")
    print("="*60)
    print(f"Parámetros: Host={host}, User={user}, Password={'[vacía]' if not password else '[configurada]'}, Port={port}")
    
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        if connection.is_connected():
            print("✓ Conexión exitosa SIN base de datos")
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION(), USER()")
            version, current_user = cursor.fetchone()
            print(f"✓ Versión de MySQL/MariaDB: {version}")
            print(f"✓ Usuario actual: {current_user}")
            cursor.close()
            connection.close()
            return True
    except Error as e:
        print(f"✗ Error: {e}")
        print("\nPosibles soluciones:")
        print("  1. Verifica que el usuario 'root' existe en MySQL")
        print("  2. Si 'root' tiene una contraseña, actualiza DB_PASSWORD en .env")
        print("  3. Intenta crear el usuario manualmente en MySQL")
        return False
    except Exception as e:
        print(f"✗ Error inesperado: {e}")
        traceback.print_exc()
        return False

def test_connection_with_db():
    """Intenta conectar CON la base de datos especificada"""
    host = os.getenv('DB_HOST', 'localhost')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    database = os.getenv('DB_NAME', 'db_verifica_bolivia')
    port = int(os.getenv('DB_PORT', 3306))
    
    print("\n" + "="*60)
    print("TEST 2: Conectar CON base de datos")
    print("="*60)
    print(f"Parámetros: Host={host}, User={user}, Database={database}, Port={port}")
    
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        if connection.is_connected():
            print(f"✓ Conexión exitosa a la base de datos '{database}'")
            connection.close()
            return True
    except Error as e:
        print(f"✗ Error: {e}")
        print(f"\nVerifica que:")
        print(f"  1. La base de datos '{database}' existe")
        print(f"  2. El usuario '{user}' tiene acceso a esta base de datos")
        print(f"  3. Ejecuta: mysql -u root -p")
        print(f"     Y luego: SHOW DATABASES;")
        return False
    except Exception as e:
        print(f"✗ Error inesperado: {e}")
        return False

def test_list_databases():
    """Lista las bases de datos disponibles"""
    host = os.getenv('DB_HOST', 'localhost')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    port = int(os.getenv('DB_PORT', 3306))
    
    print("\n" + "="*60)
    print("TEST 3: Listar bases de datos disponibles")
    print("="*60)
    
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print("✓ Bases de datos disponibles:")
            for db in databases:
                print(f"  - {db[0]}")
            cursor.close()
            connection.close()
            return True
    except Exception as e:
        print(f"✗ Error al listar bases de datos: {e}")
        return False

if __name__ == "__main__":
    print("DIAGNÓSTICO COMPLETO DE CONEXIÓN A MYSQL")
    print("=" * 60)
    
    # Verificar conectividad TCP
    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', 3306))
    
    print(f"Verificando conectividad TCP a {host}:{port}...")
    try:
        sock = socket.create_connection((host, port), timeout=3)
        sock.close()
        print("✓ Conexión TCP exitosa")
    except Exception as e:
        print(f"✗ Error de conexión TCP: {e}")
        print("  MySQL no está corriendo o el puerto está bloqueado")
        exit(1)
    
    # Ejecutar tests
    test1_ok = test_connection_without_db()
    
    if test1_ok:
        test2_ok = test_connection_with_db()
        if test2_ok:
            print("\n" + "="*60)
            print("✓ TODAS LAS PRUEBAS EXITOSAS")
            print("="*60)
        else:
            print("\nIntentando listar bases de datos...")
            test_list_databases()
    else:
        print("\n✗ No se puede conectar con las credenciales especificadas")
        print("  Revisa que el usuario y contraseña sean correctos")
