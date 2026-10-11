"""
Vector store service using ChromaDB for RAG (Retrieval-Augmented Generation).
"""
import uuid
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
import structlog

from app.core.config import settings
from app.services.ollama_service import ollama_service, OllamaService

logger = structlog.get_logger(__name__)


@dataclass
class Document:
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class SearchResult:
    document: Document
    score: float


class VectorStoreService:
    """Service for managing vector embeddings and similarity search."""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: Optional[str] = None,
        ollama: Optional[OllamaService] = None,
    ):
        self.host = host or settings.CHROMA_HOST
        self.port = port or settings.CHROMA_PORT
        self.collection_name = collection_name or settings.CHROMA_COLLECTION
        self.ollama = ollama or ollama_service
        self._client: Optional[chromadb.HttpClient] = None
        self._collection = None
    
    async def _get_client(self) -> chromadb.HttpClient:
        if self._client is None:
            self._client = chromadb.HttpClient(
                host=self.host,
                port=self.port,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        return self._client
    
    async def _get_collection(self):
        """Get or create the collection."""
        if self._collection is None:
            client = await self._get_client()
            self._collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection
    
    async def initialize(self) -> None:
        """Initialize the vector store."""
        await self._get_collection()
        logger.info("Vector store initialized", collection=self.collection_name)
    
    async def add_documents(
        self,
        documents: List[Document],
        batch_size: int = 100,
    ) -> List[str]:
        """Add documents to the vector store with embeddings."""
        if not documents:
            return []
        
        collection = await self._get_collection()
        ids = []
        contents = []
        metadatas = []
        embeddings = []
        
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            # Generate embeddings for batch
            texts = [doc.content for doc in batch]
            batch_embeddings = await self.ollama.embeddings(texts)
            
            for doc, embedding in zip(batch, batch_embeddings):
                doc_id = doc.id or str(uuid.uuid4())
                ids.append(doc_id)
                contents.append(doc.content)
                metadatas.append(doc.metadata)
                embeddings.append(embedding)
            
            # Add batch to collection
            collection.add(
                ids=ids[-len(batch):],
                documents=contents[-len(batch):],
                metadatas=metadatas[-len(batch):],
                embeddings=embeddings[-len(batch):],
            )
            
            logger.debug("Added batch to vector store", count=len(batch))
        
        logger.info("Documents added to vector store", count=len(documents))
        return ids
    
    async def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        include_embeddings: bool = False,
    ) -> List[SearchResult]:
        """Search for similar documents."""
        collection = await self._get_collection()
        
        # Generate query embedding
        query_embedding = await self.ollama.embeddings(query)
        
        # Search
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=filter_metadata,
            include=["documents", "metadatas", "distances", "embeddings"] if include_embeddings else ["documents", "metadatas", "distances"],
        )
        
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                doc = Document(
                    id=doc_id,
                    content=results["documents"][0][i],
                    metadata=results["metadatas"][0][i],
                    embedding=results["embeddings"][0][i] if include_embeddings and results.get("embeddings") else None,
                )
                # Convert distance to similarity score (cosine distance -> similarity)
                score = 1.0 - results["distances"][0][i]
                search_results.append(SearchResult(document=doc, score=score))
        
        return search_results
    
    async def search_by_embedding(
        self,
        embedding: List[float],
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search using a pre-computed embedding."""
        collection = await self._get_collection()
        
        results = collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"],
        )
        
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                doc = Document(
                    id=doc_id,
                    content=results["documents"][0][i],
                    metadata=results["metadatas"][0][i],
                )
                score = 1.0 - results["distances"][0][i]
                search_results.append(SearchResult(document=doc, score=score))
        
        return search_results
    
    async def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID."""
        collection = await self._get_collection()
        results = collection.get(ids=[doc_id], include=["documents", "metadatas", "embeddings"])
        
        if results["ids"] and results["ids"][0]:
            return Document(
                id=results["ids"][0],
                content=results["documents"][0],
                metadata=results["metadatas"][0],
                embedding=results["embeddings"][0] if results.get("embeddings") else None,
            )
        return None
    
    async def update_document(self, document: Document) -> bool:
        """Update an existing document."""
        collection = await self._get_collection()
        
        # Generate new embedding if content changed
        embedding = document.embedding
        if embedding is None:
            embeddings = await self.ollama.embeddings(document.content)
            embedding = embeddings[0] if embeddings else None
        
        collection.update(
            ids=[document.id],
            documents=[document.content],
            metadatas=[document.metadata],
            embeddings=[embedding] if embedding else None,
        )
        return True
    
    async def delete_documents(self, ids: List[str]) -> bool:
        """Delete documents by IDs."""
        collection = await self._get_collection()
        collection.delete(ids=ids)
        return True
    
    async def delete_by_metadata(self, filter_metadata: Dict[str, Any]) -> bool:
        """Delete documents matching metadata filter."""
        collection = await self._get_collection()
        collection.delete(where=filter_metadata)
        return True
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        collection = await self._get_collection()
        count = collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
        }
    
    async def reset_collection(self) -> bool:
        """Delete and recreate the collection (use with caution)."""
        client = await self._get_client()
        client.delete_collection(name=self.collection_name)
        self._collection = None
        await self._get_collection()
        return True


# Singleton instance
vector_store_service = VectorStoreService()


async def get_vector_store() -> VectorStoreService:
    """Dependency for FastAPI to get vector store service."""
    await vector_store_service.initialize()
    return vector_store_service