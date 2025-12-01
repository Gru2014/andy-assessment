from flask import Blueprint, jsonify
from app.models import DiscoveryJob

bp = Blueprint('jobs', __name__, url_prefix='/jobs')

@bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get job status by ID"""
    job = DiscoveryJob.query.get_or_404(job_id)
    
    return jsonify({
        'id': job.id,
        'collection_id': job.collection_id,
        'status': job.status.value,
        'progress': job.progress,
        'current_step': job.current_step,
        'error_message': job.error_message,
        'created_at': job.created_at.isoformat() if job.created_at else None,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None
    })

@bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'topic-discovery-api'
    })

