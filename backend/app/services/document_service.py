from typing import List, Dict, Any, Optional
from app import db
from app.models import Collection, Document, DocumentEmbedding
from app.services.genai_service import GenAIService
import os

class DocumentService:
    """Service for document ingestion"""
    
    def __init__(self):
        self.genai = GenAIService()
    
    def add_document(self, collection_id: int, content: str, title: Optional[str] = None, 
                    file_path: Optional[str] = None, file_type: Optional[str] = None) -> Document:
        """Add a document to a collection"""
        collection = Collection.query.get_or_404(collection_id)
        
        # Extract title from content if not provided
        if not title:
            title = content[:100].split('\n')[0].strip() or f"Document {len(collection.documents) + 1}"
        
        document = Document(
            collection_id=collection_id,
            title=title,
            content=content,
            file_path=file_path,
            file_type=file_type
        )
        
        db.session.add(document)
        db.session.commit()
        
        # Generate embedding
        try:
            embedding_vec = self.genai.get_embedding(content[:8000])
            embedding = DocumentEmbedding(
                document_id=document.id,
                embedding=embedding_vec,
                model=self.genai.embedding_model
            )
            db.session.add(embedding)
            db.session.commit()
        except Exception as e:
            # Document is saved even if embedding fails
            print(f"Failed to generate embedding for document {document.id}: {str(e)}")
        
        return document
    
    def add_documents_batch(self, collection_id: int, documents: List[Dict[str, Any]]) -> List[Document]:
        """Add multiple documents to a collection"""
        added_docs = []
        for doc_data in documents:
            doc = self.add_document(
                collection_id=collection_id,
                content=doc_data.get('content', ''),
                title=doc_data.get('title'),
                file_path=doc_data.get('file_path'),
                file_type=doc_data.get('file_type')
            )
            added_docs.append(doc)
        return added_docs

