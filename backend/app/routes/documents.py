from flask import Blueprint, request, jsonify
from app import db
from app.models import Collection, Document
from app.services.document_service import DocumentService
from app.services.discovery_job import DiscoveryJobService
from rq import Queue
from redis import Redis
import os

bp = Blueprint('documents', __name__, url_prefix='/collections')
redis_conn = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
q = Queue(connection=redis_conn)

document_service = DocumentService()
discovery_service = DiscoveryJobService()

@bp.route('/<int:collection_id>/documents', methods=['POST'])
def add_documents(collection_id):
    """Add documents to a collection (triggers incremental update)"""
    collection = Collection.query.get_or_404(collection_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Handle single document or batch
    if 'content' in data:
        # Single document
        documents = [data]
    elif 'documents' in data:
        # Batch
        documents = data['documents']
    else:
        return jsonify({'error': 'Invalid format. Provide "content" or "documents" array'}), 400
    
    # Add documents
    added_docs = document_service.add_documents_batch(collection_id, documents)
    
    # Trigger incremental discovery
    incremental = data.get('trigger_discovery', True)
    if incremental:
        from app.workers import run_discovery_job
        rq_job = q.enqueue(run_discovery_job, collection_id, incremental=True)
        
        from app.models import DiscoveryJob, JobStatus
        job = DiscoveryJob(
            collection_id=collection_id,
            status=JobStatus.PENDING,
            rq_job_id=rq_job.id
        )
        db.session.add(job)
        db.session.commit()
    
    return jsonify({
        'documents_added': len(added_docs),
        'document_ids': [doc.id for doc in added_docs],
        'incremental_discovery_triggered': incremental
    }), 201

@bp.route('/<int:collection_id>/documents', methods=['GET'])
def list_documents(collection_id):
    """List documents in a collection"""
    collection = Collection.query.get_or_404(collection_id)
    documents = Document.query.filter_by(collection_id=collection_id).all()
    
    return jsonify([{
        'id': doc.id,
        'title': doc.title,
        'content_preview': doc.content[:200] if doc.content else '',
        'file_type': doc.file_type,
        'created_at': doc.created_at.isoformat() if doc.created_at else None
    } for doc in documents])

@bp.route('/<int:collection_id>/documents/<int:document_id>', methods=['GET'])
def get_document(collection_id, document_id):
    """Get a document by ID"""
    document = Document.query.filter_by(
        id=document_id,
        collection_id=collection_id
    ).first_or_404()
    
    # Return HTML for HTMX requests, JSON for API requests
    if request.headers.get('HX-Request'):
        from flask import render_template
        return render_template('document_preview.html', document=document)
    
    return jsonify({
        'id': document.id,
        'title': document.title,
        'content': document.content,
        'file_type': document.file_type,
        'created_at': document.created_at.isoformat() if document.created_at else None
    })

