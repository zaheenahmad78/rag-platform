# 🧠 Multi-Tenant RAG-as-a-Service (FastAPI)

A secure, multi-tenant Retrieval-Augmented Generation (RAG) API built with FastAPI. This service allows you to create isolated tenants, upload documents (PDFs/TXT), and query them using an LLM while ensuring strict data isolation between tenants.

## 🚀 Live Demo (Click to Test)

> 🔗 **Base URL:** `https://your-deployed-app-url.com` *(Replace this with your actual deployed URL)*
> 
> 🧪 **Interactive API Docs:** `https://your-deployed-app-url.com/docs`

[![Swagger UI](https://img.shields.io/badge/Swagger-UI-blue)](https://your-deployed-app-url.com/docs)

---

## ✨ Key Features

- **🔐 Tenant Isolation:** Data from one tenant is completely invisible to others.
- **📄 Document Ingestion:** Upload and index text files/PDFs for specific tenants.
- **🤖 RAG Querying:** Ask questions based on uploaded documents using state-of-the-art LLMs.
- **🗂️ CRUD Operations:** Create, read, and delete tenants and their documents via a clean API.
- **⚡ FastAPI Performance:** Built with async support for high throughput.

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Web Framework:** FastAPI
- **Vector Database:** ChromaDB *(or replace with Pinecone/Qdrant)*
- **LLM Integration:** OpenAI GPT-4 / Llama 3 *(Local via Ollama)*
- **Data Storage:** SQLite *(for tenant metadata)*
- **Deployment:** Render / Railway / Docker

---

## 📋 Prerequisites

Before running this project, make sure you have the following installed:

- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- An OpenAI API Key (if using OpenAI as the LLM) or [Ollama](https://ollama.com/) installed locally for free usage.

---

## 🔧 Installation & Setup

Follow these steps to run the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/multi-tenant-rag.git
cd multi-tenant-rag
