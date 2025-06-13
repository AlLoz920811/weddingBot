# 🌐 RAG Pipeline «Wedding Info» — Visión General

Este script implementa un **flujo extremo-a-extremo** que transforma un PDF alojado en Azure Blob Storage en documentos indexados con vectores para un asistente conversacional (Sofía) sobre Azure AI Search + Azure OpenAI.

---

## 1. Arquitectura de alto nivel

```mermaid
flowchart TD
  subgraph Azure
    A["Blob Storage – Bronze\n(PDF)"] -->|PDF| B["Azure Document Intelligence\n(prebuilt-read)"]
    B -->|texto| C["Blob Storage – Silver\n(Texto limpio)"]
    C -->|normalizado| D["Blob Storage – Gold\n(JSON segmentado)"]
    D -->|JSON| E["Azure OpenAI\n(Embeddings)"]
    E -->|vectores| F["Azure AI Search\n(Index)"]
  end
  F -->|Consulta híbrida| G["Azure OpenAI GPT-4o\n(Asistente Sofía)"]


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




 

