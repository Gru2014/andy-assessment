import pytest
from app import create_app, db
from app.models import Collection, Document, Topic, DocumentTopic, TopicRelationship, TopicInsight, DiscoveryJob, JobStatus

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def sample_collection(app):
    """Create a sample collection"""
    collection = Collection(name='Test Collection', description='Test')
    db.session.add(collection)
    db.session.commit()
    return collection

@pytest.fixture
def sample_documents(app, sample_collection):
    """Create sample documents"""
    docs = []
    for i in range(5):
        doc = Document(
            collection_id=sample_collection.id,
            title=f'Document {i+1}',
            content=f'This is the content of document {i+1}. It contains some text about topic {i % 3}.'
        )
        db.session.add(doc)
        docs.append(doc)
    db.session.commit()
    return docs

@pytest.fixture
def sample_topics(app, sample_collection):
    """Create sample topics"""
    topics = []
    for i in range(3):
        topic = Topic(
            collection_id=sample_collection.id,
            name=f'Topic {i+1}',
            cluster_id=i,
            document_count=2,
            size_score=0.4
        )
        db.session.add(topic)
        topics.append(topic)
    db.session.commit()
    return topics

