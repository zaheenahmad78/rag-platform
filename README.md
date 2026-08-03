# Multi-Tenant RAG Service
[Description of what this project does]

## 🚀 Features
- Multi-tenant document isolation
- Upload and index PDF/Doc files
- RAG-based querying using [LLM Name]

## 🛠️ Tech Stack
- Backend: FastAPI
- Vector DB: ChromaDB
- LLM: OpenAI / Llama 3

## 📋 Prerequisites
- Python 3.10+
- OpenAI API Key (if using OpenAI)

## 🔧 Installation
1. Clone the repo: `git clone ...`
2. Install dependencies: `pip install -r requirements.txt`
3. Setup environment variables: Create `.env` file and add API keys.

## ▶️ How to Run
```bash
uvicorn app.main:app --reload
