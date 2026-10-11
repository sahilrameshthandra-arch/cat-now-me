"""
Document management endpoints for RAG (Retrieval-Augmented Generation).
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import structlog
import uuid
from datetime import datetime

from app.services.vector_store import vector_store_service, Document, SearchResult
from app.services.ollama_service import ollama_service
from app.core.security import get_current_active_user, TokenData
from app.core.config import settings

logger = structlog.get_logger(__name__)

router = APIRouter()


# Request/Response Models
class DocumentCreate(BaseModel):
    content: str = Field(..., description="Document content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Document metadata")
    id: Optional[str] = Field(default=None, description="Optional custom ID")


class DocumentResponse(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]
    created_at: str


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    n_results: int = Field(default=5, ge=1, le=50, description="Number of results")
    filter_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filter")


class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    total_results: int


class IngestResponse(BaseModel):
    document_ids: List[str]
    count: int
    message: str


# Helper functions
def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from uploaded file based on content type."""
    content = file.file.read()
    file.file.seek(0)
    
    if file.content_type == "text/plain":
        return content.decode("utf-8")
    elif file.content_type == "application/pdf":
        # TODO: Add PyPDF2 or pdfplumber for PDF extraction
        return "[PDF content extraction not implemented]"
    elif file.content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        # TODO: Add python-docx for DOCX extraction
        return "[DOCX content extraction not implemented]"
    elif file.content_type == "text/markdown":
        return content.decode("utf-8")
    else:
        # Try to decode as text
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return f"[Binary file: {file.filename}]"


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        # Try to break at sentence boundary
        if end < len(text):
            last_period = text.rfind(".", start, end)
            last_newline = text.rfind("\n", start, end)
            break_point = max(last_period, last_newline)
            if break_point > start:
                end = break_point + 1
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


@router.post("", response_model=DocumentResponse, status_code=201)
async def create_document(
    document: DocumentCreate,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Create a new document in the vector store."""
    doc_id = document.id or str(uuid.uuid4())
    
    doc = Document(
        id=doc_id,
        content=document.content,
        metadata={
            **document.metadata,
            "created_by": current_user.user_id,
            "created_at": datetime.utcnow().isoformat(),
        },
    )
    
    ids = await vector_store_service.add_documents([doc])
    
    return DocumentResponse(
        id=ids[0],
        content=document.content,
        metadata=doc.metadata,
        created_at=doc.metadata["created_at"],
    )


@router.post("/upload", response_model=IngestResponse)
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    chunk_size: int = Form(default=1000),
    chunk_overlap: int = Form(default=200),
    metadata: Optional[str] = Form(default="{}"),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Upload and ingest multiple files into the vector store."""
    import json
    
    try:
        base_metadata = json.loads(metadata) if metadata else {}
    except json.JSONDecodeError:
        base_metadata = {}
    
    base_metadata.update({
        "uploaded_by": current_user.user_id,
        "uploaded_at": datetime.utcnow().isoformat(),
    })
    
    all_documents = []
    
    for file in files:
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File {file.filename} exceeds maximum size of {settings.MAX_FILE_SIZE} bytes"
            )
        
        text = extract_text_from_file(file)
        if not text or text.startswith("["):
            logger.warning("Could not extract text from file", filename=file.filename)
            continue
        
        chunks = chunk_text(text, chunk_size, chunk_overlap)
        
        for i, chunk in enumerate(chunks):
            doc = Document(
                id=str(uuid.uuid4()),
                content=chunk,
                metadata={
                    **base_metadata,
                    "source_file": file.filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "content_type": file.content_type,
                },
            )
            all_documents.append(doc)
    
    if not all_documents:
        raise HTTPException(status_code=400, detail="No valid content extracted from files")
    
    # Add to vector store
    doc_ids = await vector_store_service.add_documents(all_documents)
    
    return IngestResponse(
        document_ids=doc_ids,
        count=len(doc_ids),
        message=f"Ingested {len(all_documents)} chunks from {len(files)} files",
    )


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Search documents using semantic similarity."""
    results = await vector_store_service.search(
        query=request.query,
        n_results=request.n_results,
        filter_metadata=request.filter_metadata,
    )
    
    return SearchResponse(
        results=[
            {
                "id": r.document.id,
                "content": r.document.content,
                "metadata": r.document.metadata,
                "score": r.score,
            }
            for r in results
        ],
        query=request.query,
        total_results=len(results),
    )


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Get a document by ID."""
    doc = await vector_store_service.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        id=doc.id,
        content=doc.content,
        metadata=doc.metadata,
        created_at=doc.metadata.get("created_at", ""),
    )


@router.put("/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: str,
    document: DocumentCreate,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Update an existing document."""
    existing = await vector_store_service.get_document(doc_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = Document(
        id=doc_id,
        content=document.content,
        metadata={
            **document.metadata,
            "updated_by": current_user.user_id,
            "updated_at": datetime.utcnow().isoformat(),
        },
    )
    
    await vector_store_service.update_document(doc)
    
    return DocumentResponse(
        id=doc.id,
        content=doc.content,
        metadata=doc.metadata,
        created_at=existing.metadata.get("created_at", ""),
    )


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: TokenData = Depends(get_current_active_user),
):
    """Delete a document."""
    await vector_store_service.delete_documents([doc_id])
    return {"message": "Document deleted", "id": doc_id}


@router.delete("")
async def delete_documents_by_filter(
    filter_metadata: Dict[str, Any],
    current_user: TokenData = Depends(get_current_active_user),
):
    """Delete documents matching metadata filter."""
    await vector_store_service.delete_by_metadata(filter_metadata)
    return {"message": "Documents deleted", "filter": filter_metadata}


@router.get("/stats/summary")
async def get_stats(current_user: TokenData = Depends(get_current_active_user)):
    """Get vector store statistics."""
    stats = await vector_store_service.get_collection_stats()
    return stats


@router.post("/reset")
async def reset_collection(current_user: TokenData = Depends(get_current_active_user)):
    """Reset the entire collection (DELETE ALL DATA)."""
    # Require admin role
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    
    await vector_store_service.reset_collection()
    return {"message": "Collection reset successfully"}