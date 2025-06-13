from fastapi import FastAPI, HTTPException, Form, Response
from pydantic import BaseModel
import uuid
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from openai import AzureOpenAI
from RAG import search_query
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI(title="WeddingBot Sofia", description="IA de Q&A para bodas")

# Cargar variables desde el archivo .env
load_dotenv()

# Configuración de Azure OpenAI Y AI Search
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_INDEX_NAME = os.getenv("AZURE_INDEX_NAME")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuración de Azure Search
search_service_endpoint = AZURE_SEARCH_ENDPOINT
index_name = AZURE_INDEX_NAME
search_api_key = AZURE_SEARCH_KEY 
api_search_version = "2024-11-01-preview"

class QueryRequest(BaseModel):
    session_id: str = None
    query: str

#creating an Azure OpenAI client
client = AzureOpenAI(
    api_key = AZURE_OPENAI_KEY,  
    api_version = "2024-02-15-preview",
    azure_endpoint = AZURE_OPENAI_ENDPOINT)

openai_client = OpenAI(api_key=OPENAI_API_KEY)

@app.get("/")
def home():
    return f"Bienvenido a {app.title}🚀"

@app.post("/chat")
def chat(request: QueryRequest):
    """
    Recibe una pregunta y devuelve una respuesta basada en RAG.
    Si no se proporciona session_id, genera uno automáticamente.
    """
    # Generar session_id si no se proporciona
    session_id = request.session_id if request.session_id else str(uuid.uuid4())
    query = request.query

    try:

        # Configuración de Azure Search
        search_service_endpoint = AZURE_SEARCH_ENDPOINT
        index_name = AZURE_INDEX_NAME
        search_api_key = AZURE_SEARCH_KEY 
        api_search_version = "2024-11-01-preview"

        context = search_query(client, query, search_api_key, search_service_endpoint, index_name, api_search_version)
        
        # Generar respuesta con GPT-4o
        system_prompt = f''' Eres **Sofía**, la organizadora profesional de eventos encargada de asistir a los invitados de la 
                             boda de Laura Guadalupe Zarazúa Arvizu y José Alberto Lozano Sánchez. 
                             Atiendes por WhatsApp usando RAG con búsqueda semántica híbrida (Top‑10).

                            🎯 **Fuente única**  
                            Solo extrae información de los **10 fragmentos** en `{context}`.  
                            Si no existe la respuesta, di literal:  
                            “Mira, no tengo la información precisa por el momento, pero reviso con los novios en un momento”
                            solicitando al usuario formular la pregunta y sugiriendo **2 temas clave** adicionales sin realizar preguntas cerradas.

                            🧭 **Tono y estilo**  
                            Cálido, empático y profesional, como una event planner con experiencia.  
                            Frases cortas, claras y directas; nada de florituras.

                            🚫 **Cero alucinaciones**   No inventes ni supongas.  
                            No muestres tu proceso de búsqueda: entrega solo la respuesta final.

                            📂 **Uso de contexto**  
                            1. Antes de responder, selecciona solo los fragmentos **relevantes** de `{context}`.   
                            2. Coordina datos coherentes (hora, lugar, acción).

                            🗺️ **Ubicaciones e imágenes**  
                            Si preguntan por un lugar, incluye:  
                            • Dirección completa  
                            • Enlace de Google Maps  

                            🔄 **Cierre proactivo**  
                            Al final, sugiere **2 temas clave** adicionales sobre la boda que el invitado 
                            podría preguntar siempre dentro del limite de la longitud de cada mensaje.   

                            🔄 **Respuestas cerradas como Si o NO por parte del usuario**  
                            Si el usuario responde con un **SI** o **NO**, responde sugiriendo **4 temas clave**. 

                            ✂️ **Límite de longitud**  
                            Cada mensaje ≤ 1600 caracteres.  
                            Si excedes, sintetiza automáticamente:  
                            • Prioriza lugar, hora, acciones, enlaces.  
                            • Usa viñetas si y solo si cabe más información y con emojis acorde al contexto.
                            '''
        
        chat_history = []
        chat_history.append({"role": "system", "content": system_prompt})
        chat_history.append({"role": "user", "content": query})         

        # Generar respuesta con gpt-4.1
        gpt_response  = openai_client.chat.completions.create(
            model = "gpt-4.1",
            messages=chat_history,  # Enviar historial completo,
            max_tokens=1000,  
            temperature=0.8,  
            top_p=0.9,  
            frequency_penalty=0,  
            presence_penalty=0,
            stop=None,  
            stream=False  
        )

        response = gpt_response.choices[0].message.content
        session_id = str(uuid.uuid4())

        # Guardar en Cosmos DB
        chat_entry = {
            "session_id": session_id,
            "query": query,
            "response": response
            }

        return chat_entry
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/webhook")
def receive_msg_wp(From: str = Form(...), Body: str = Form(...)):
    """ Endpoint para recibir mensajes desde WhatsApp vía Twilio """
    print(f"Mensaje recibido de {From}: {Body}")
    
    respuesta_bot = call_api_bot(Body)
    respuesta_twilio = MessagingResponse()
    msg = respuesta_twilio.message(respuesta_bot)

    # Nueva lógica para agregar imagen del jardín/recepción/terreno
    keywords1 = ["jardín", "recepción", "terreno", "jardin", "recepcion", "fiesta", "peda", "evento"]
    if any(palabra in Body.lower() for palabra in keywords1):
        msg.media("https://sa19920811dev.blob.core.windows.net/images/foto_terreno.png")
    
    # Nueva lógica para agregar imagen de la ceremonia religiosa
    keywords2 = ["misa", "ceremonia", "ceremonia reliogiosa", "parroquia", "parroquía", "iglesia"]
    if any(palabra in Body.lower() for palabra in keywords2):
        msg.media("https://sa19920811dev.blob.core.windows.net/images/foto_iglesia.jpg")

    return Response(content=str(respuesta_twilio), media_type="application/xml")

def call_api_bot(texto):
    """ Llama a la API del chatbot en Azure App Service y devuelve la respuesta """
    url = "https://weddingbotapp-escqeufmd8cbd3e8.eastus2-01.azurewebsites.net/chat"  
    payload = {"query": texto}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_json = response.json()
        return response_json.get("response", "Disculpe, no entendí su mensaje.")
    except Exception as e:
        return f"Error al comunicar con el bot: {str(e)}"
    
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload