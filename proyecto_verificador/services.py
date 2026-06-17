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

        if not busqueda or 'results' not in busqueda or not busqueda['results']:
            raise ValueError("No se encontraron resultados en la búsqueda de Tavily")

        # Extraemos y recortamos contextos
        contextos = [resultado['content'][:800] for resultado in busqueda['results'] if 'content' in resultado]
        fuentes = [resultado['url'] for resultado in busqueda['results'] if 'url' in resultado]

        if not contextos:
            raise ValueError("No se encontraron contextos válidos para la noticia")

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
            "veredicto": "Falso" o "Verdadero" o "Verificado Pero En Desarrollo" o "Contradictorio",
            "confianza": (número del 1 al 100),
            "analisis": "Explicación breve",
            "fuentes_verificadas": {json.dumps(fuentes)}
        }}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )

        if not chat_completion or not chat_completion.choices:
            raise ValueError("La IA no devolvió una respuesta válida")

        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error en services texto: {e}")
        return json.dumps({"veredicto": "Contradictorio", "confianza": 0, "analisis": str(e)})

def analizar_imagen_falsa(imagen_bytes):
    # FIX #2: Usar gemini-2.0-flash que es más estable y tiene mejor soporte
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    img = Image.open(io.BytesIO(imagen_bytes))
    
    # Prompt sincronizado con la tabla 'verificacion_imagen'
    prompt = """
    Analiza esta imagen para detectar si es falsa o manipulada por IA.
    Responde ÚNICAMENTE en formato JSON:
    {
        "analisis_visual": "Descripción breve",
        "probabilidad_ia": "Alta/Media/Baja",
        "veredicto_imagen": "Falso" o "Verdadero" o "Engañoso" o "No determinado"
    }
    """
    
    response = model.generate_content([prompt, img])
    # Limpiamos posibles backticks de Markdown si la IA los agrega
    return response.text.replace("```json", "").replace("```", "").strip()

def verificar_link(url):
    try:
        # Extraer contenido de la URL usando search() (compatible con tavily==1.1.0)
        busqueda = tavily_client.search(query=url, search_depth="basic", max_results=3)
        contextos = [r.get('content', '')[:500] for r in busqueda.get('results', []) if r.get('content')]
        contexto_web = " ".join(contextos) if contextos else "No se encontró contenido relevante."
        
        # Prompt sincronizado con la tabla 'verificacion_link'
        prompt = f"""
        Analiza el contenido de este enlace y responde en JSON:
        CONTENIDO: {contexto_web[:1000]}
        
        Estructura JSON:
        {{
            "veredicto": "Falso" o "Verdadero" o "Engañoso" o "No determinado",
            "resumen_contenido": "Breve descripción",
            "confiabilidad_sitio": "Alta/Media/Baja",
            "confianza": (número del 1 al 100)
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