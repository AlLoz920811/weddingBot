# 📌 **Lista de Endpoints Creados en la API FastAPI Desplegada en Azure**  

Después de organizar y estructurar el código, la API ahora tiene **dos módulos principales**:
- **Módulo `webhook`** → Para manejar la integración con Twilio WhatsApp API.
- **Módulo `chat`** → Para manejar consultas con GPT-4o utilizando Azure OpenAI.

Aquí están **todos los endpoints creados** y su respectiva funcionalidad. 🎯🔥  

---

## 📌 **Resumen de la API FastAPI en Azure**
| **Método** | **Ruta** | **Descripción** |
|-----------|---------|----------------|
| **GET** | `/` | 🏠 **Endpoint principal** que devuelve un mensaje de bienvenida. |
| **POST** | `/chat` | 💬 **Realiza consultas a GPT-4.1** y recibe respuestas basadas en Retrieval-Augmented Generation (RAG). |
| **POST** | `/webhook` | 📥 **Recibe mensajes entrantes de WhatsApp** y los procesa en FastAPI. |




 

