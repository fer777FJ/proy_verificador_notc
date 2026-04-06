import pandas as pd
import mysql.connector
from mysql.connector import Error
import os

def conectar_db():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='', # Tu contraseña de MariaDB
            database='db_verifica_bolivia'
        )
        return conexion
    except Error as e:
        print(f"❌ Error de conexión: {e}")
        return None

def mapear_etiqueta(veredicto):
    """
    Transforma el veredicto en un número para entrenamiento de IA.
    1 = Verdad / 0 = Falso / -1 = Ignorar para entrenamiento limpio
    """
    v = str(veredicto).lower()
    if 'verdadero' in v:
        return 1
    elif 'falso' in v:
        return 0
    else:
        return -1 # 'Engañoso' o 'Contradictorio' se marcan para revisión

def generar_dataset():
    conn = conectar_db()
    if not conn: return

    print("📊 Extrayendo datos de MariaDB...")
    
    try:
        # 1. Cargar tablas en DataFrames de Pandas
        df_texto = pd.read_sql("SELECT titulo, contenido, veredicto, confianza, fecha FROM verificacion_texto", conn)
        df_link = pd.read_sql("SELECT titulo, url_link as contenido, veredicto, confianza, fecha FROM verificacion_link", conn)
        
        # 2. Unificar los datos (Texto y Links suelen ser los más útiles para NLP)
        dataset = pd.concat([df_texto, df_link], ignore_index=True)

        if dataset.empty:
            print("⚠️ No hay datos suficientes para generar el CSV.")
            return

        # 3. Aplicar ingeniería de características (Labeling)
        dataset['label'] = dataset['veredicto'].apply(mapear_etiqueta)

        # 4. Crear carpeta de datasets si no existe
        if not os.path.exists('datasets'):
            os.makedirs('datasets')

        # 5. Guardar Versión Completa (Para auditoría)
        dataset.to_csv('datasets/historial_completo_bolivia.csv', index=False, encoding='utf-8-sig')

        # 6. Guardar Versión de Entrenamiento (Solo 0s y 1s, limpio de ruido)
        df_train = dataset[dataset['label'] != -1][['contenido', 'label']]
        df_train.to_csv('datasets/dataset_entrenamiento_ia.csv', index=False, encoding='utf-8-sig')

        print(f"✅ ¡Dataset generado con éxito!")
        print(f"   - Total registros: {len(dataset)}")
        print(f"   - Listos para entrenar (Verdadero/Falso): {len(df_train)}")
        print(f"   - Archivo guardado en: /datasets/dataset_entrenamiento_ia.csv")

    except Exception as e:
        print(f"❌ Error durante la generación: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    generar_dataset()