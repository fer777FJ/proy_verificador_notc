import os
import json
import io
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient
import google.generativeai as genai
from PIL import Image

# Cargar variables de entorno
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Inicializamos los clientes
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def verificar_noticia_texto(titular, contenido):
    try:
        # 1. Búsqueda limitada para ahorrar tokens (Rate Limit Groq)
        consulta_busqueda = f"veracidad de: {titular}"
        busqueda = tavily_client.search(query=consulta_busqueda, search_depth="basic", max_results=2)
        
        # Extraemos y recortamos contextos
        contextos = [resultado['content'][:800] for resultado in busqueda['results']]
        fuentes = [resultado['url'] for resultado in busqueda['results']]
        
        # 2. Prompt sincronizado con la tabla 'verificacion_texto'
        prompt = f"""
        Eres un experto en fact-checking en Bolivia. 
        Analiza la noticia basándote en las evidencias.
        
        NOTICIA:
        Titular: {titular}
        Contenido: {contenido[:500]}
        
        EVIDENCIAS:
        {contextos}
        
        Responde estrictamente en JSON con esta estructura:
        {{
            "veredicto": "Falso", "Verdadero", "Verificado Pero En Desarrollo", "Contradictorio",
            "confianza": (número del 1 al 100),
            "analisis": "Explicación breve",
            "fuentes_verificadas": {fuentes}
        }}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error en services texto: {e}")
        return json.dumps({"veredicto": "Contradictorio", "confianza": 0, "analisis": "Error de conexión"})

def analizar_imagen_falsa(imagen_bytes):
    # Usamos gemini-1.5-flash por estabilidad y compatibilidad
    model = genai.GenerativeModel('gemini-1.5-flash') 
    
    img = Image.open(io.BytesIO(imagen_bytes))
    
    # Prompt sincronizado con la tabla 'verificacion_imagen'
    prompt = """
    Analiza esta imagen para detectar si es falsa o manipulada por IA.
    Responde ÚNICAMENTE en formato JSON:
    {
        "analisis_visual": "Descripción breve",
        "probabilidad_ia": "Alta/Media/Baja",
        "veredicto": "Falso", "Verdadero", "Engañoso", "No determinado"
    }
    """
    
    response = model.generate_content([prompt, img])
    # Limpiamos posibles backticks de Markdown si la IA los agrega
    return response.text.replace("```json", "").replace("```", "").strip()

def verificar_link(url):
    try:
        # Extraer contenido de la URL
        contexto_web = tavily_client.get_search_context(query=url, search_depth="basic")
        
        # Prompt sincronizado con la tabla 'verificacion_link'
        prompt = f"""
        Analiza el contenido de este enlace y responde en JSON:
        CONTENIDO: {contexto_web[:1000]}
        
        Estructura JSON:
        {{
            "veredicto": "Falso", "Verdadero", "Engañoso", "No determinado",
            "resumen_contenido": "Breve descripción",
            "confiabilidad_sitio": "Alta/Media/Baja",
            "confianza": 70
        }}
        """
        
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error en services link: {e}")
        return json.dumps({"veredicto": "No determinado", "confianza": 0, "resumen_contenido": "Error al procesar link"})