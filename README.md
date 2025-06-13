# 📌 **Lista de Endpoints Creados en la API FastAPI Desplegada en Azure**  

Después de organizar y estructurar el código, la API ahora tiene **dos módulos principales**:
- **Módulo `whatsapp`** → Para manejar la integración con Twilio WhatsApp API.
- **Módulo `gpt`** → Para manejar consultas con GPT-4o utilizando Azure OpenAI.

Aquí están **todos los endpoints creados** y su respectiva funcionalidad. 🎯🔥  

---

## ✅ **1. Endpoints de WhatsApp (Twilio)**
| **Método** | **Ruta** | **Descripción** |
|-----------|---------|----------------|
| **POST** | `/whatsapp/send` | 📩 **Envía un mensaje de WhatsApp** a un número de teléfono utilizando Twilio. |
| **POST** | `/whatsapp/webhook` | 📥 **Recibe mensajes entrantes de WhatsApp** y los procesa en FastAPI. |

---

## ✅ **2. Endpoints de GPT-4o (Azure OpenAI)**
| **Método** | **Ruta** | **Descripción** |
|-----------|---------|----------------|
| **POST** | `/gpt/chat` | 💬 **Realiza consultas a GPT-4o** y recibe respuestas basadas en Retrieval-Augmented Generation (RAG). |
| **GET** | `/gpt/history/{session_id}` | 📜 **Recupera el historial de chat** de una sesión específica. |

---

## ✅ **3. Endpoints Generales**
| **Método** | **Ruta** | **Descripción** |
|-----------|---------|----------------|
| **GET** | `/` | 🏠 **Endpoint principal** que devuelve un mensaje de bienvenida. |

---

## 📌 **Resumen de la API FastAPI en Azure**
| **Grupo de Endpoints** | **Función** |
|----------------|--------------|
| **`/whatsapp/*`** | Maneja la integración con Twilio WhatsApp API |
| **`/gpt/*`** | Maneja la integración con GPT-4o y RAG |
| **`/`** | Página de bienvenida |


 

