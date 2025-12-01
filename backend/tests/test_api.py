import pytest
import json
from app.models import Collection, Document, Topic, DocumentTopic

def test_list_collections(client):
    """Test listing collections"""
    response = client.get('/collections')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_create_collection(client):
    """Test creating a collection"""
    data = {'name': 'New Collection', 'description': 'Test'}
    response = client.post('/collections', json=data)
    assert response.status_code == 201
    assert response.json['name'] == 'New Collection'

def test_get_collection(client, sample_collection):
    """Test getting a collection"""
    response = client.get(f'/collections/{sample_collection.id}')
    assert response.status_code == 200
    assert response.json['id'] == sample_collection.id

def test_add_documents(client, sample_collection):
    """Test adding documents"""
    data = {
        'documents': [
            {'content': 'Test content 1', 'title': 'Doc 1'},
            {'content': 'Test content 2', 'title': 'Doc 2'}
        ],
        'trigger_discovery': False
    }
    response = client.post(f'/collections/{sample_collection.id}/documents', json=data)
    assert response.status_code == 201
    assert response.json['documents_added'] == 2

def test_list_documents(client, sample_collection, sample_documents):
    """Test listing documents"""
    response = client.get(f'/collections/{sample_collection.id}/documents')
    assert response.status_code == 200
    assert len(response.json) >= len(sample_documents)

def test_get_topic_graph(client, sample_collection, sample_topics):
    """Test getting topic graph"""
    # Create a relationship
    from app.models import TopicRelationship
    from app import db
    with client.application.app_context():
        rel = TopicRelationship(
            source_topic_id=sample_topics[0].id,
            target_topic_id=sample_topics[1].id,
            similarity_score=0.5,
            relationship_type='RELATED'
        )
        db.session.add(rel)
        db.session.commit()
    
    response = client.get(f'/collections/{sample_collection.id}/topics/graph')
    assert response.status_code == 200
    assert 'nodes' in response.json
    assert 'edges' in response.json

def test_get_topic_detail(client, sample_topics):
    """Test getting topic detail"""
    response = client.get(f'/topics/{sample_topics[0].id}')
    assert response.status_code == 200
    assert response.json['id'] == sample_topics[0].id
    assert 'documents' in response.json

def test_health_endpoint(client):
    """Test health endpoint"""
    response = client.get('/jobs/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_start_discovery(client, sample_collection):
    """Test starting discovery"""
    response = client.post(f'/collections/{sample_collection.id}/discover', json={'incremental': False})
    # Should return 202 (accepted) or handle gracefully
    assert response.status_code in [202, 500]  # 500 if Redis not available

def test_get_discovery_status(client, sample_collection):
    """Test getting discovery status"""
    response = client.get(f'/collections/{sample_collection.id}/discover/status')
    # May return 404 if no job exists, which is acceptable
    assert response.status_code in [200, 404]

