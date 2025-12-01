import pytest
from app.services.topic_discovery import TopicDiscoveryService
from app.services.relationship_service import RelationshipService
from app.services.insight_service import InsightService
from app.services.document_service import DocumentService
from app.models import Collection, Document

def test_document_service_add_document(app, sample_collection):
    """Test adding a document"""
    with app.app_context():
        service = DocumentService()
        doc = service.add_document(
            collection_id=sample_collection.id,
            content='Test document content',
            title='Test Document'
        )
        assert doc.id is not None
        assert doc.title == 'Test Document'
        assert doc.collection_id == sample_collection.id

def test_document_service_batch(app, sample_collection):
    """Test batch document addition"""
    with app.app_context():
        service = DocumentService()
        docs_data = [
            {'content': 'Content 1', 'title': 'Doc 1'},
            {'content': 'Content 2', 'title': 'Doc 2'}
        ]
        docs = service.add_documents_batch(sample_collection.id, docs_data)
        assert len(docs) == 2
        assert docs[0].title == 'Doc 1'

def test_topic_discovery_service_structure(app, sample_collection, sample_documents):
    """Test topic discovery service structure"""
    with app.app_context():
        service = TopicDiscoveryService()
        # Note: This test checks structure, actual discovery requires embeddings
        assert service.genai is not None

def test_relationship_service_structure(app):
    """Test relationship service structure"""
    with app.app_context():
        service = RelationshipService()
        assert service.genai is not None

def test_insight_service_structure(app):
    """Test insight service structure"""
    with app.app_context():
        service = InsightService()
        assert service.genai is not None

