import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

host = os.getenv('DB_HOST', 'localhost')
user = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASSWORD', '')
database = os.getenv('DB_NAME', 'db_verifica_bolivia')
port = int(os.getenv('DB_PORT', 3306))

print("="*60)
print("TEST CON PYMYSQL (librería alternativa)")
print("="*60)

try:
    import pymysql
    print("✓ PyMySQL está instalado")
    print(f"\nIntentando conectar con PyMySQL...")
    print(f"Parámetros: Host={host}, User={user}, Password={'[vacía]' if not password else '[configurada]'}, Port={port}")
    
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )
    
    print("✓ ¡Conexión exitosa con PyMySQL!")
    cursor = connection.cursor()
    cursor.execute("SELECT VERSION(), USER()")
    version, current_user = cursor.fetchone()
    print(f"✓ Versión de MySQL: {version}")
    print(f"✓ Usuario actual: {current_user}")
    cursor.close()
    connection.close()
    
except ImportError:
    print("✗ PyMySQL no está instalado")
    print("  Instálalo con: pip install pymysql")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
