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

app = FastAPI(title="WeddingBot Sofia", description="Wedding Q&A AI Assistant")

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI and AI Search configuration
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_INDEX_NAME = os.getenv("AZURE_INDEX_NAME")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Azure Search configuration
search_service_endpoint = AZURE_SEARCH_ENDPOINT
index_name = AZURE_INDEX_NAME
search_api_key = AZURE_SEARCH_KEY 
api_search_version = "2024-11-01-preview"

class QueryRequest(BaseModel):
    session_id: str = None
    query: str

# Creating an Azure OpenAI client
client = AzureOpenAI(
    api_key = AZURE_OPENAI_KEY,  
    api_version = "2024-02-15-preview",
    azure_endpoint = AZURE_OPENAI_ENDPOINT)

openai_client = OpenAI(api_key=OPENAI_API_KEY)

@app.get("/")
def home():
    return f"Welcome to {app.title}🚀"

@app.post("/chat")
def chat(request: QueryRequest):
    """
    Receives a question and returns a RAG-based response.
    If no session_id is provided, one is automatically generated.
    """
    # Generate session_id if not provided
    session_id = request.session_id if request.session_id else str(uuid.uuid4())
    query = request.query

    try:
        # Azure Search configuration
        search_service_endpoint = AZURE_SEARCH_ENDPOINT
        index_name = AZURE_INDEX_NAME
        search_api_key = AZURE_SEARCH_KEY 
        api_search_version = "2024-11-01-preview"

        context = search_query(client, query, search_api_key, search_service_endpoint, index_name, api_search_version)
        
        # Generate response with GPT-4.1
        system_prompt = f'''You are **Sofia**, the professional event organizer in charge of assisting the guests of 
                         the wedding of Laura Guadalupe Zarazúa Arvizu and José Alberto Lozano Sánchez. 
                         You attend via WhatsApp using RAG with hybrid semantic search (Top-10).

                        🎯 **Single Source**  
                        Only extract information from the **10 fragments** in `{context}`.  
                        If the answer doesn't exist, say literally:  
                        "I don't have the precise information at the moment, but I'll check with the couple right away"
                        asking the user to phrase the question and suggesting **2 key topics** without asking closed questions.

                        🧭 **Tone and Style**  
                        Warm, empathetic, and professional, like an experienced event planner.  
                        Short, clear, and direct phrases; no frills.

                        🚫 **No Hallucinations**  Don't make up or assume anything.  
                        Don't show your search process: deliver only the final answer.

                        📂 **Context Usage**  
                        1. Before responding, select only the **relevant** fragments from `{context}`.   
                        2. Coordinate consistent data (time, place, action).

                        🗺️ **Locations and Images**  
                        If they ask about a place, include:  
                        • Complete address  
                        • Google Maps link  

                        🔄 **Proactive Closing**  
                        At the end, suggest **2 key topics** about the wedding that the guest 
                        might ask about, always within the message length limit.   

                        🔄 **User's Yes/No Responses**  
                        If the user responds with **YES** or **NO**, respond by suggesting **4 key topics**. 
                        """

        chat_history = []
        chat_history.append({"role": "system", "content": system_prompt})
        chat_history.append({"role": "user", "content": query})         

        # Generate response with gpt-4.1
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
    """ Endpoint to receive messages from WhatsApp via Twilio """
    print(f"Message received from {From}: {Body}")
    
    respuesta_bot = call_api_bot(Body)
    respuesta_twilio = MessagingResponse()
    msg = respuesta_twilio.message(respuesta_bot)

    # New logic to add image of garden/reception/venue
    keywords1 = ["garden", "reception", "venue", "garden", "reception", "party", "event"]
    if any(word in Body.lower() for word in keywords1):
        msg.media("https://sa19920811dev.blob.core.windows.net/images/foto_terreno.png")
    
    # New logic to add image of the religious ceremony
    keywords2 = ["mass", "ceremony", "religious ceremony", "parish", "parish", "church"]
    if any(word in Body.lower() for word in keywords2):
        msg.media("https://sa19920811dev.blob.core.windows.net/images/foto_iglesia.jpg")

    return Response(content=str(respuesta_twilio), media_type="application/xml")

def call_api_bot(texto):
    """ Calls the chatbot API in Azure App Service and returns the response """
    url = "https://weddingbotapp-escqeufmd8cbd3e8.eastus2-01.azurewebsites.net/chat"  
    payload = {"query": texto}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_json = response.json()
        return response_json.get("response", "I couldn't process your request at the moment.")
    except Exception as e:
        return f"Error calling the bot: {str(e)}"
    
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload