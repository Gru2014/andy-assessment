"""Background worker functions for RQ"""
from app import create_app, db
from app.services.discovery_job import DiscoveryJobService

def run_discovery_job(collection_id: int, incremental: bool = False):
    """RQ worker function for running discovery jobs"""
    app = create_app()
    with app.app_context():
        service = DiscoveryJobService()
        return service.run_discovery(collection_id, incremental=incremental)

