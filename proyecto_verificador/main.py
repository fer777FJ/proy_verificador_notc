from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import os
import uuid
import services
from database import guardar_verificacion, obtener_historial

# 1. Configuración de la App
app = FastAPI(title="VerificaBolivia AI | Sistema de Fact-Checking")

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

# --- RUTA DEL HISTORIAL ---
@app.get("/historial")
async def get_historial():
    try:
        data = obtener_historial()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- RUTAS DE VERIFICACIÓN ---

@app.post("/verificar-texto")
async def verificar_texto(request: NoticiaRequest):
    try:
        print(f"Recibido titular: {request.titular}")
        print(f"Recibido contenido: {request.contenido[:100]}...")

        resultado_json = services.verificar_noticia_texto(request.titular, request.contenido)
        print(f"Respuesta de services.verificar_noticia_texto: {resultado_json}")

        res_dict = json.loads(resultado_json)
        
        # Validar campos requeridos
        if 'veredicto' not in res_dict or 'confianza' not in res_dict:
            raise ValueError("Respuesta inválida de la API: faltan campos requeridos")

        # Mapear valores no válidos de veredicto
        valores_validos = ['Falso', 'Verdadero', 'Engañoso', 'No determinado']
        veredicto = res_dict.get('veredicto')
        if veredicto not in valores_validos:
            print(f"Advertencia: El veredicto '{veredicto}' no es válido. Se asignará 'No determinado'.")
            veredicto = "No determinado"

        datos_db = {
            'titulo': request.titular[:250], 
            'contenido': request.contenido,
            'veredicto': veredicto,
            'confianza': float(res_dict.get('confianza', 50)) / 100
        }
        print(f"Datos a guardar en la base de datos: {datos_db}")

        guardar_verificacion('texto', datos_db)
        print("Datos guardados exitosamente en la base de datos.")
        
        return res_dict
    except Exception as e:
        print(f"Error en verificación de texto: {e}")
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {e}")

@app.post("/verificar-link")
async def verificar_link(request: LinkRequest):
    try:
        resultado_json = services.verificar_link(request.url)
        res_dict = json.loads(resultado_json)
        
        # Validar campos requeridos
        if 'veredicto' not in res_dict or 'confianza' not in res_dict:
            raise ValueError("Respuesta inválida de la API")
        
        datos_db = {
            'titulo': "Verificación de Enlace Externo",
            'url_link': request.url,
            'veredicto': res_dict.get('veredicto'),
            'confianza': float(res_dict.get('confianza', 50)) / 100
        }
        guardar_verificacion('link', datos_db)
        
        return res_dict
    except Exception as e:
        print(f"Error en verificación de link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verificar-imagen")
async def verificar_imagen(file: UploadFile = File(...)):
    try:
        extension = os.path.splitext(file.filename)[1]
        nombre_archivo = f"{uuid.uuid4()}{extension}"
        ruta_relativa = os.path.join("static", "img", nombre_archivo)
        
        os.makedirs(os.path.dirname(ruta_relativa), exist_ok=True)

        contenido_bytes = await file.read()
        with open(ruta_relativa, "wb") as f:
            f.write(contenido_bytes)

        resultado_raw = services.analizar_imagen_falsa(contenido_bytes)
        resultado_limpio = resultado_raw.replace("```json", "").replace("```", "").strip()
        res_dict = json.loads(resultado_limpio)

        # Validar campos requeridos
        if 'veredicto_imagen' not in res_dict:
            raise ValueError("Campo 'veredicto_imagen' no encontrado en respuesta")

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