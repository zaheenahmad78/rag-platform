# 🧠 Multi-Tenant RAG-as-a-Service (FastAPI)

A secure, production-ready, multi-tenant Retrieval-Augmented Generation (RAG) API built with FastAPI. This service allows you to create isolated tenants, upload documents (PDFs/TXT), and query them using an LLM while ensuring strict data isolation between tenants.

## 🚀 Live Demo (Click to Test)

🔗 **Base URL:** [https://rag-platform-awm3.onrender.com](https://rag-platform-awm3.onrender.com)
🧪 **Interactive API Docs (Swagger UI):** [https://rag-platform-awm3.onrender.com/docs](https://rag-platform-awm3.onrender.com/docs)

*Note: Since this is hosted on Render's free tier, the instance might take 50-60 seconds to "wake up" on the first request.*

## 🏗️ How It Works
1. **Create Tenant:** A new company gets a unique ID, namespace, and API Key.
2. **Upload Document:** The document is split into chunks, converted into embeddings, and stored in the Vector Database (ChromaDB) under that specific tenant's namespace.
3. **Query:** When a question is asked, the system searches *only* within that tenant's namespace. The retrieved context is sent to the LLM (Groq) to generate an accurate, hallucination-free answer.

## ✨ Key Features

- 🔐 **Tenant Isolation:** Data from one tenant is completely invisible to others (strict API key & namespace validation).
- 📄 **Document Ingestion:** Upload and index text files/PDFs for specific tenants.
- 🤖 **RAG Querying:** Ask questions based on uploaded documents using state-of-the-art LLMs (via Groq).
- 🗂️ **CRUD Operations:** Create, read, and delete tenants and their documents via a clean API.
- ⚡ **FastAPI Performance:** Built with async support for high throughput.

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Language** | Python 3.11+ |
| **Web Framework** | FastAPI |
| **Vector Database** | ChromaDB (Easily swappable with Pinecone/Qdrant) |
| **LLM Integration** | Groq API (Llama 3) / OpenAI GPT-4 |
| **Data Storage** | SQLite (for tenant metadata) |
| **Deployment** | Render (Docker) |

## 📋 Prerequisites

Before running this project locally, make sure you have the following installed:
- Python 3.10+
- Git
- A **Groq API Key** (Free tier available at console.groq.com) OR an OpenAI API Key.

## 🔧 Installation & Setup

Follow these steps to run the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/zaheenahmad78/rag-platform.git
cd rag-platform
