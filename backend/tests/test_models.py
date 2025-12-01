import pytest
from app.models import Collection, Document, Topic, DocumentTopic, TopicRelationship, TopicInsight, DiscoveryJob, JobStatus

def test_collection_creation(app):
    """Test collection creation"""
    with app.app_context():
        collection = Collection(name='Test Collection', description='Test')
        assert collection.name == 'Test Collection'
        assert collection.description == 'Test'

def test_document_creation(app, sample_collection):
    """Test document creation"""
    with app.app_context():
        doc = Document(
            collection_id=sample_collection.id,
            title='Test Doc',
            content='Test content'
        )
        assert doc.collection_id == sample_collection.id
        assert doc.title == 'Test Doc'

def test_topic_creation(app, sample_collection):
    """Test topic creation"""
    with app.app_context():
        topic = Topic(
            collection_id=sample_collection.id,
            name='Test Topic',
            cluster_id=1,
            document_count=5
        )
        assert topic.name == 'Test Topic'
        assert topic.document_count == 5

def test_document_topic_assignment(app, sample_collection, sample_documents, sample_topics):
    """Test document-topic assignment"""
    with app.app_context():
        assignment = DocumentTopic(
            document_id=sample_documents[0].id,
            topic_id=sample_topics[0].id,
            relevance_score=0.85,
            is_primary=True
        )
        assert assignment.relevance_score == 0.85
        assert assignment.is_primary is True

def test_topic_relationship(app, sample_topics):
    """Test topic relationship"""
    with app.app_context():
        rel = TopicRelationship(
            source_topic_id=sample_topics[0].id,
            target_topic_id=sample_topics[1].id,
            similarity_score=0.75,
            relationship_type='RELATED'
        )
        assert rel.similarity_score == 0.75
        assert rel.relationship_type == 'RELATED'

def test_discovery_job(app, sample_collection):
    """Test discovery job"""
    with app.app_context():
        job = DiscoveryJob(
            collection_id=sample_collection.id,
            status=JobStatus.PENDING
        )
        assert job.status == JobStatus.PENDING

