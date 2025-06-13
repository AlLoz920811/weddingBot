from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from collections import defaultdict
import uuid
import os
from openai import AzureOpenAI
from RAG import search_query
###

app = FastAPI(title="WeddingBot Sofia", description="IA de Q&A para bodas")

# Diccionario en memoria para almacenar los historiales de cada usuario
chat_history = defaultdict(list)

# Modelo de entrada
class QueryRequest(BaseModel):
    session_id: str = None  # Ahora es opcional
    query: str

@app.get("/")
def home():
    return f"Bienvenido a {app.title}🚀"

@app.post("/chat/")
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
        search_service_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        index_name = os.getenv("AZURE_INDEX_NAME")
        search_api_key = os.getenv("AZURE_SEARCH_KEY")
        api_search_version = "2024-11-01-preview"

        #creating an Azure OpenAI client
        client = AzureOpenAI(
        api_key = os.getenv("AZURE_OPENAI_KEY"),  
        api_version = "2024-02-15-preview",
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") 
        )

        context = search_query(client, query, search_api_key, search_service_endpoint, index_name, api_search_version)

        # Generar respuesta con GPT-4o
        system_prompt = f"""Actua como una event planner profesional encargada de resolver a cada una de las dudas relacionadas la boda de Laura y Alberto, 
                            respondiendo con un tono amable y servicial con todo lo relacionado a dicha boda. 
                            Utiliza como variable de contexto {context} y no respondas a preguntas diferentes a la variable de contexto. 
                            Cuando respondas con bullets coloca un emoji deacuerdo al contexto de cada uno.
                            Sugiere alguno de los temas mas relevantes del evento en cada una de tus respuestas para guiar al usuario.
                            Cuando des informacion sobre direcciones e indicaciones de lugares, proporciona los links de google maps 
                            acorde al lugar que el usuario solicite"""
        

            # Obtener historial de mensajes de la sesión (si no existe, inicializarlo)
        if not chat_history[session_id]:
            chat_history[session_id] = [{"role": "system", "content": system_prompt}]

        # Agregar la consulta del usuario al historial
        chat_history[session_id].append({"role": "user", "content": request.query})       

        gpt_response  = client.chat.completions.create(
            model = "gpt-4o",
            messages=chat_history[session_id],  # Enviar historial completo,
            max_tokens=5000,  
            temperature=0.7,  
            top_p=0.9,  
            frequency_penalty=0,  
            presence_penalty=0,
            stop=None,  
            stream=False  
        )
        
        response = gpt_response.choices[0].message.content

        # Guardar en historial
        chat_history[session_id].append({"query": query, "response": response})

        return {
            "session_id": session_id,
            "query": query,
            "answer": response,
            "history": chat_history[session_id]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/history/{session_id}")
def get_chat_history(session_id: str):
    """
    Recupera el historial de chat de la sesión persistente global.
    """
    if session_id not in chat_history:
        raise HTTPException(status_code=404, detail="No hay historial disponible")

    return {"session_id": session_id, "history": chat_history[session_id]}