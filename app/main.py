from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
from datetime import datetime

app = FastAPI(
    title="Multi-Tenant RAG Platform",
    description="RAG-as-a-Service with tenant isolation",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= In-Memory Storage (Temporary) =============
tenants_db = {}
documents_db = {}
usage_db = {}

# ============= Models =============
class TenantCreate(BaseModel):
    name: str
    namespace: str
    plan: str = "free"

class TenantResponse(BaseModel):
    id: str
    name: str
    namespace: str
    api_key: str
    plan: str
    rate_limit: int
    created_at: str

class QueryRequest(BaseModel):
    query: str
    limit: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    tenant_id: str

# ============= Root Endpoints =============

@app.get("/")
async def root():
    return {
        "message": "Multi-Tenant RAG Platform",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ============= Tenant APIs =============

@app.post("/api/v1/tenants/", response_model=TenantResponse)
async def create_tenant(tenant_data: TenantCreate):
    """Create a new tenant"""
    
    # Check if namespace exists
    for tenant in tenants_db.values():
        if tenant["namespace"] == tenant_data.namespace:
            raise HTTPException(status_code=400, detail="Namespace already exists")
    
    # Generate API key
    api_key = f"tk_{uuid.uuid4().hex[:32]}"
    
    # Plan limits
    plan_limits = {
        "free": 100,
        "pro": 1000,
        "enterprise": 10000
    }
    
    tenant_id = str(uuid.uuid4())
    tenant = {
        "id": tenant_id,
        "name": tenant_data.name,
        "namespace": tenant_data.namespace,
        "api_key": api_key,
        "plan": tenant_data.plan,
        "rate_limit": plan_limits.get(tenant_data.plan, 100),
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
    
    tenants_db[tenant_id] = tenant
    documents_db[tenant_id] = []
    
    return tenant

@app.get("/api/v1/tenants/")
async def list_tenants():
    """List all tenants"""
    return list(tenants_db.values())

@app.get("/api/v1/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    """Get tenant by ID"""
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@app.delete("/api/v1/tenants/{tenant_id}")
async def delete_tenant(tenant_id: str):
    """Delete a tenant"""
    if tenant_id not in tenants_db:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    del tenants_db[tenant_id]
    if tenant_id in documents_db:
        del documents_db[tenant_id]
    if tenant_id in usage_db:
        del usage_db[tenant_id]
    
    return {"status": "success", "message": "Tenant deleted"}

# ============= Document APIs =============

@app.post("/api/v1/documents/upload/{tenant_id}")
async def upload_document(
    tenant_id: str,
    file: UploadFile = File(...),
    x_api_key: Optional[str] = Header(None)
):
    """Upload a document for a tenant"""
    
    # Verify tenant exists
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Verify API key
    if x_api_key and x_api_key != tenant["api_key"]:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    if not tenant.get("is_active", True):
        raise HTTPException(status_code=403, detail="Tenant is inactive")
    
    # Read file content
    content = await file.read()
    
    # Check file size (max 10MB)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Max 10MB")
    
    # Simple processing
    doc_id = str(uuid.uuid4())
    
    # Try to extract text based on file type
    file_content = ""
    if file.filename.lower().endswith('.txt'):
        try:
            file_content = content.decode('utf-8')
        except:
            file_content = "Cannot decode file content"
    elif file.filename.lower().endswith('.pdf'):
        file_content = "PDF content - would need PyPDF2 for extraction"
    else:
        file_content = "Unsupported file type for preview"
    
    doc = {
        "id": doc_id,
        "tenant_id": tenant_id,
        "filename": file.filename,
        "file_size": len(content),
        "file_type": file.filename.split('.')[-1] if '.' in file.filename else 'unknown',
        "status": "ready",
        "uploaded_at": datetime.now().isoformat(),
        "content_preview": file_content[:500] if len(file_content) > 500 else file_content,
        "full_content": file_content
    }
    
    if tenant_id not in documents_db:
        documents_db[tenant_id] = []
    documents_db[tenant_id].append(doc)
    
    # Track usage
    if tenant_id not in usage_db:
        usage_db[tenant_id] = {"documents": 0, "queries": 0, "storage_bytes": 0}
    usage_db[tenant_id]["documents"] += 1
    usage_db[tenant_id]["storage_bytes"] += len(content)
    
    return {
        "status": "success",
        "doc_id": doc_id,
        "filename": file.filename,
        "file_size": len(content),
        "message": "Document uploaded successfully"
    }

@app.get("/api/v1/documents/{tenant_id}")
async def list_documents(tenant_id: str):
    """List all documents for a tenant"""
    
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    docs = documents_db.get(tenant_id, [])
    return [
        {
            "id": d["id"],
            "filename": d["filename"],
            "file_size": d["file_size"],
            "file_type": d.get("file_type", "unknown"),
            "status": d["status"],
            "uploaded_at": d["uploaded_at"]
        }
        for d in docs
    ]

@app.delete("/api/v1/documents/{tenant_id}/{doc_id}")
async def delete_document(tenant_id: str, doc_id: str):
    """Delete a specific document"""
    
    if tenant_id not in tenants_db:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    docs = documents_db.get(tenant_id, [])
    for i, doc in enumerate(docs):
        if doc["id"] == doc_id:
            del docs[i]
            return {"status": "success", "message": "Document deleted"}
    
    raise HTTPException(status_code=404, detail="Document not found")

# ============= Query API =============

@app.post("/api/v1/query/{tenant_id}", response_model=QueryResponse)
async def query_documents(
    tenant_id: str,
    request: QueryRequest,
    x_api_key: Optional[str] = Header(None)
):
    """Query documents for a tenant"""
    
    # Verify tenant exists
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Verify API key
    if not x_api_key or x_api_key != tenant["api_key"]:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    
    # Rate limiting
    if tenant_id not in usage_db:
        usage_db[tenant_id] = {"documents": 0, "queries": 0}
    
    usage_db[tenant_id]["queries"] = usage_db[tenant_id].get("queries", 0) + 1
    
    # Check rate limit
    if usage_db[tenant_id]["queries"] > tenant.get("rate_limit", 100):
        raise HTTPException(
            status_code=429, 
            detail=f"Rate limit exceeded. Max {tenant.get('rate_limit', 100)} queries per hour"
        )
    
    # Get tenant documents
    docs = documents_db.get(tenant_id, [])
    
    if not docs:
        return QueryResponse(
            answer="No documents found for this tenant.",
            sources=[],
            tenant_id=tenant_id
        )
    
    # Simple keyword search
    query_words = request.query.lower().split()
    
    if not query_words:
        return QueryResponse(
            answer="Please provide a valid query.",
            sources=[],
            tenant_id=tenant_id
        )
    
    results = []
    
    for doc in docs:
        if doc["status"] == "ready":
            content = doc.get("full_content", doc.get("content_preview", "")).lower()
            
            # Calculate relevance score
            matched_words = 0
            for word in query_words:
                if word in content:
                    matched_words += 1
            
            # Also check filename
            filename_match = sum(1 for word in query_words if word in doc["filename"].lower())
            matched_words += filename_match * 0.5
            
            if matched_words > 0:
                score = matched_words / len(query_words) if query_words else 0
                results.append({
                    "doc_id": doc["id"],
                    "filename": doc["filename"],
                    "text": doc.get("content_preview", "")[:300],
                    "score": min(score, 1.0),
                    "matched_keywords": matched_words
                })
    
    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:request.limit]
    
    if not results:
        answer = "No relevant documents found for your query. Try different keywords."
    else:
        answer_parts = []
        for r in results[:3]:
            if r["score"] > 0.2:
                answer_parts.append(f"From '{r['filename']}': {r['text'][:200]}")
        
        if answer_parts:
            answer = "Based on the documents:\n\n" + "\n\n".join(answer_parts)
        else:
            answer = f"Found {len(results)} document(s) but none have high relevance."
    
    return QueryResponse(
        answer=answer,
        sources=results,
        tenant_id=tenant_id
    )

# ============= Usage Metrics =============

@app.get("/api/v1/metrics/{tenant_id}")
async def get_usage_metrics(tenant_id: str):
    """Get usage metrics for a tenant"""
    
    tenant = tenants_db.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    usage = usage_db.get(tenant_id, {"documents": 0, "queries": 0, "storage_bytes": 0})
    
    storage_mb = round(usage.get("storage_bytes", 0) / (1024 * 1024), 2)
    
    return {
        "tenant_id": tenant_id,
        "tenant_name": tenant["name"],
        "tenant_namespace": tenant["namespace"],
        "plan": tenant["plan"],
        "documents_uploaded": usage.get("documents", 0),
        "queries_made": usage.get("queries", 0),
        "storage_used_mb": storage_mb,
        "rate_limit_per_hour": tenant.get("rate_limit", 100),
        "queries_remaining": max(0, tenant.get("rate_limit", 100) - usage.get("queries", 0)),
        "is_active": tenant.get("is_active", True)
    }

@app.get("/api/v1/metrics/all")
async def get_all_metrics():
    """Get metrics for all tenants"""
    metrics = []
    for tenant_id in tenants_db:
        metrics.append(await get_usage_metrics(tenant_id))
    return metrics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)