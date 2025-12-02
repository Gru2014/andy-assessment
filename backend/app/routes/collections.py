from flask import Blueprint, request, jsonify
from app import db
from app.models import Collection
from app.services.document_service import DocumentService
from app.services.discovery_job import DiscoveryJobService
from rq import Queue
from redis import Redis
import os

bp = Blueprint('collections', __name__, url_prefix='/collections')
redis_conn = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
q = Queue(connection=redis_conn)

document_service = DocumentService()
discovery_service = DiscoveryJobService()

@bp.route('', methods=['GET'])
def list_collections():
    """List all collections"""
    collections = Collection.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'created_at': c.created_at.isoformat() if c.created_at else None,
        'document_count': len(c.documents),
        'topic_count': len(c.topics)
    } for c in collections])

@bp.route('', methods=['POST'])
def create_collection():
    """Create a new collection"""
    data = request.get_json()
    collection = Collection(
        name=data.get('name', 'Untitled Collection'),
        description=data.get('description')
    )
    db.session.add(collection)
    db.session.commit()
    return jsonify({
        'id': collection.id,
        'name': collection.name,
        'description': collection.description
    }), 201

@bp.route('/<int:collection_id>', methods=['GET'])
def get_collection(collection_id):
    """Get a collection by ID"""
    collection = Collection.query.get_or_404(collection_id)
    return jsonify({
        'id': collection.id,
        'name': collection.name,
        'description': collection.description,
        'created_at': collection.created_at.isoformat() if collection.created_at else None,
        'document_count': len(collection.documents),
        'topic_count': len(collection.topics)
    })

@bp.route('/<int:collection_id>', methods=['DELETE'])
def delete_collection(collection_id):
    """Delete a collection and all its data"""
    collection = Collection.query.get_or_404(collection_id)
    # Cascade delete will handle documents, topics, relationships, etc.
    db.session.delete(collection)
    db.session.commit()
    return jsonify({'message': 'Collection deleted successfully'}), 200

@bp.route('/<int:collection_id>/discover', methods=['POST'])
def start_discovery(collection_id):
    """Start topic discovery for a collection (background job)"""
    collection = Collection.query.get_or_404(collection_id)
    # Handle both JSON and form data (for HTMX)
    if request.is_json:
        data = request.get_json() or {}
    else:
        # HTMX sends form data
        data = request.form.to_dict()
        # Also check for JSON in request data (hx-vals sends JSON)
        if not data and request.data:
            try:
                import json
                data = json.loads(request.data.decode('utf-8'))
            except:
                pass
    
    incremental = data.get('incremental', False)
    if isinstance(incremental, str):
        incremental = incremental.lower() in ('true', '1', 'yes')
    elif isinstance(incremental, bool):
        incremental = incremental
    else:
        incremental = bool(incremental)
    
    # Create job record first
    from app.models import DiscoveryJob, JobStatus
    job = DiscoveryJob(
        collection_id=collection_id,
        status=JobStatus.PENDING,
        rq_job_id=None  # Will be set after enqueue
    )
    db.session.add(job)
    db.session.commit()
    
    # Enqueue the job with job_id
    from app.workers import run_discovery_job
    try:
        rq_job = q.enqueue(run_discovery_job, collection_id, incremental, job.id)
        # Update job with RQ job ID
        job.rq_job_id = rq_job.id
        db.session.commit()
    except Exception as e:
        # If enqueue fails, mark job as failed
        job.status = JobStatus.FAILED
        job.error_message = f"Failed to enqueue job: {str(e)}"
        db.session.commit()
        return jsonify({
            'error': 'Failed to start discovery job',
            'message': str(e)
        }), 500
    
    # Return HTML fragment for HTMX or JSON for API
    if request.headers.get('HX-Request'):
        from flask import render_template
        from app.models import DiscoveryJob
        job_data = {
            'id': job.id,
            'status': job.status.value,
            'progress': job.progress,
            'current_step': job.current_step,
            'error_message': job.error_message
        }
        return render_template('job_status.html', job=job_data, collection_id=collection_id)
    
    return jsonify({
        'job_id': job.id,
        'rq_job_id': rq_job.id,
        'status': job.status.value,
        'collection_id': collection_id
    }), 202

@bp.route('/<int:collection_id>/discover/status', methods=['GET'])
def get_discovery_status(collection_id):
    """Get discovery job status for a collection"""
    from app.models import DiscoveryJob
    job = DiscoveryJob.query.filter_by(collection_id=collection_id).order_by(
        DiscoveryJob.created_at.desc()
    ).first()
    
    if not job:
        return jsonify({'error': 'No discovery job found'}), 404
    
    return jsonify({
        'job_id': job.id,
        'status': job.status.value,
        'progress': job.progress,
        'current_step': job.current_step,
        'error_message': job.error_message,
        'created_at': job.created_at.isoformat() if job.created_at else None,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None
    })

