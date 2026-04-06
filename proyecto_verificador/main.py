from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import os
import uuid
import services  # Tu lógica de Tavily, Groq y Gemini
from database import guardar_verificacion, obtener_historial  # Tu conexión a MariaDB

# 1. Configuración de la App
app = FastAPI(title="VerificaBolivia AI | Sistema de Fact-Checking")

# Montar archivos estáticos para el CSS, JS e Imágenes subidas
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- MODELOS DE DATOS ---
class NoticiaRequest(BaseModel):
    titular: str
    contenido: str

class LinkRequest(BaseModel):
    url: str

# --- RUTAS DE NAVEGACIÓN ---
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

# --- RUTA DEL HISTORIAL (PASO 4) ---
@app.get("/historial")
async def get_historial():
    try:
        data = obtener_historial()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- RUTAS DE VERIFICACIÓN (PASO 3: PERSISTENCIA) ---

@app.post("/verificar-texto")
async def verificar_texto(request: NoticiaRequest):
    try:
        # Llamada a la lógica en services.py (Tavily + Groq)
        resultado_json = services.verificar_noticia_texto(request.titular, request.contenido)
        res_dict = json.loads(resultado_json)
        
        # Guardar en MariaDB
        datos_db = {
            'titulo': request.titular[:250], 
            'contenido': request.contenido,
            'veredicto': res_dict.get('veredicto'),
            'confianza': float(res_dict.get('confianza', 0)) / 100
        }
        guardar_verificacion('texto', datos_db)
        
        return res_dict
    except Exception as e:
        print(f"Error en verificación de texto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verificar-link")
async def verificar_link(request: LinkRequest):
    try:
        # Llamada a la lógica en services.py (Tavily + Groq)
        resultado_json = services.verificar_link(request.url)
        res_dict = json.loads(resultado_json)
        
        # Guardar en MariaDB
        datos_db = {
            'titulo': "Verificación de Enlace Externo",
            'url_link': request.url,
            'veredicto': res_dict.get('veredicto'),
            'confianza': 0.7 # Valor estimado si Groq no devuelve score exacto
        }
        guardar_verificacion('link', datos_db)
        
        return res_dict
    except Exception as e:
        print(f"Error en verificación de link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verificar-imagen")
async def verificar_imagen(file: UploadFile = File(...)):
    try:
        # 1. Guardar archivo físico en la ruta que definiste
        extension = os.path.splitext(file.filename)[1]
        nombre_archivo = f"{uuid.uuid4()}{extension}"
        ruta_relativa = os.path.join("static", "img", nombre_archivo)
        
        # Asegurar que la carpeta existe
        os.makedirs(os.path.dirname(ruta_relativa), exist_ok=True)

        contenido_bytes = await file.read()
        with open(ruta_relativa, "wb") as f:
            f.write(contenido_bytes)

        # 2. Analizar con Gemini (en services.py)
        resultado_raw = services.analizar_imagen_falsa(contenido_bytes)
        # Limpieza de JSON por si la IA agrega backticks
        resultado_limpio = resultado_raw.replace("```json", "").replace("```", "").strip()
        res_dict = json.loads(resultado_limpio)

        # 3. Guardar en MariaDB
        datos_db = {
            'ruta_img': ruta_relativa, 
            'descripcion': res_dict.get('analisis_visual', 'Imagen analizada'),
            'veredicto': res_dict.get('veredicto_imagen'),
            'confianza': 0.9 if res_dict.get('probabilidad_ia') == 'Alta' else 0.5
        }
        guardar_verificacion('imagen', datos_db)
        
        return res_dict
    except Exception as e:
        print(f"Error en verificación de imagen: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Ejecución: uvicorn main:app --reload