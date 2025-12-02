"""Background worker functions for RQ"""
from app import create_app, db
from app.services.discovery_job import DiscoveryJobService
import logging

logger = logging.getLogger(__name__)

def run_discovery_job(collection_id: int, incremental: bool = False, job_id: int = None):
    """RQ worker function for running discovery jobs"""
    app = create_app()
    with app.app_context():
        try:
            logger.info(f"Starting discovery job: collection_id={collection_id}, incremental={incremental}, job_id={job_id}")
            service = DiscoveryJobService()
            result = service.run_discovery(collection_id, incremental=incremental, job_id=job_id)
            logger.info(f"Discovery job completed: collection_id={collection_id}, job_id={job_id}")
            return result
        except Exception as e:
            logger.error(f"Discovery job failed: collection_id={collection_id}, job_id={job_id}, error={str(e)}")
            raise

