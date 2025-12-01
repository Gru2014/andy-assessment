from typing import Dict, Any, Optional
from app import db
from app.models import Collection, DiscoveryJob, JobStatus
from app.services.topic_discovery import TopicDiscoveryService
from app.services.relationship_service import RelationshipService
from app.services.insight_service import InsightService
from datetime import datetime
import traceback

class DiscoveryJobService:
    """Service for running topic discovery as a background job"""
    
    def __init__(self):
        self.topic_discovery = TopicDiscoveryService()
        self.relationship_service = RelationshipService()
        self.insight_service = InsightService()
    
    def run_discovery(self, collection_id: int, incremental: bool = False, job_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Run the full discovery pipeline.
        Updates job status and progress throughout.
        """
        try:
            # Get or create job
            if job_id:
                job = DiscoveryJob.query.get(job_id)
            else:
                job = DiscoveryJob.query.filter_by(collection_id=collection_id).order_by(
                    DiscoveryJob.created_at.desc()
                ).first()
            
            if not job:
                job = DiscoveryJob(
                    collection_id=collection_id,
                    status=JobStatus.PENDING
                )
                db.session.add(job)
                db.session.commit()
            
            # Update job status
            job.status = JobStatus.RUNNING
            job.progress = 0.0
            job.current_step = "Starting discovery"
            db.session.commit()
            
            # Step 1: Discover topics
            job.current_step = "Discovering topics"
            job.progress = 0.2
            db.session.commit()
            
            result = self.topic_discovery.discover_topics(collection_id, incremental=incremental)
            topics = result['topics']
            
            # Step 2: Build relationships
            job.current_step = "Building relationships"
            job.progress = 0.5
            db.session.commit()
            
            relationships = self.relationship_service.build_relationships(collection_id)
            
            # Step 3: Generate insights
            job.current_step = "Generating insights"
            job.progress = 0.7
            db.session.commit()
            
            topic_ids = [topic.id for topic in topics]
            insights = self.insight_service.generate_insights_batch(topic_ids)
            
            # Step 4: Recalculate relevance scores
            job.current_step = "Calculating relevance scores"
            job.progress = 0.9
            db.session.commit()
            
            self.topic_discovery.calculate_relevance_scores(collection_id)
            
            # Complete
            job.status = JobStatus.SUCCEEDED
            job.progress = 1.0
            job.current_step = "Completed"
            job.completed_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'status': 'success',
                'topics_count': len(topics),
                'relationships_count': len(relationships),
                'insights_count': len(insights)
            }
            
        except Exception as e:
            # Update job with error
            if job:
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                job.current_step = f"Error: {str(e)}"
                db.session.commit()
            
            raise Exception(f"Discovery job failed: {str(e)}\n{traceback.format_exc()}")

