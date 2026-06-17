#!/usr/bin/env python
"""
Script para verificar que todas las dependencias funcionan correctamente
antes de ejecutar el servidor FastAPI.
"""
import os
from dotenv import load_dotenv

print("="*60)
print("VERIFICACIÓN DE DEPENDENCIAS ANTES DE INICIAR SERVIDOR")
print("="*60)

# Cargar variables de entorno
load_dotenv()

# Paso 1: Verificar PyMySQL
print("\n1. Verificando PyMySQL...")
try:
    import pymysql
    print("   ✓ PyMySQL está instalado")
except ImportError:
    print("   ✗ PyMySQL NO está instalado")
    print("   Instálalo con: pip install pymysql")
    exit(1)

# Paso 2: Verificar FastAPI
print("\n2. Verificando FastAPI...")
try:
    import fastapi
    print("   ✓ FastAPI está instalado")
except ImportError:
    print("   ✗ FastAPI NO está instalado")
    print("   Instálalo con: pip install fastapi")
    exit(1)

# Paso 3: Verificar Uvicorn
print("\n3. Verificando Uvicorn...")
try:
    import uvicorn
    print("   ✓ Uvicorn está instalado")
except ImportError:
    print("   ✗ Uvicorn NO está instalado")
    print("   Instálalo con: pip install uvicorn")
    exit(1)

# Paso 4: Verificar conexión a la base de datos
print("\n4. Verificando conexión a base de datos...")
try:
    from database import conectar_db
    conn = conectar_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"   ✓ Conexión exitosa a MariaDB")
        print(f"   ✓ Versión: {version}")
        cursor.close()
        conn.close()
    else:
        print("   ✗ No se pudo conectar a la base de datos")
        exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Paso 5: Verificar que la base de datos tiene las tablas necesarias
print("\n5. Verificando tablas en la base de datos...")
try:
    from database import conectar_db
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    required_tables = ['verificacion_texto', 'verificacion_link', 'verificacion_imagen']
    found_tables = [table[0] for table in tables]
    
    for table in required_tables:
        if table in found_tables:
            print(f"   ✓ Tabla '{table}' existe")
        else:
            print(f"   ✗ Tabla '{table}' NO existe")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

print("\n" + "="*60)
print("✓ ¡TODAS LAS VERIFICACIONES EXITOSAS!")
print("="*60)
print("\nPara iniciar el servidor, ejecuta:")
print("  uvicorn main:app --reload")
print("\nO simplemente:")
print("  python main.py")
print("="*60)
