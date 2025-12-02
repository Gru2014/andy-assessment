"""Script to delete current collection, load all documents, and run discovery"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Collection
from app.services.document_service import DocumentService
from app.services.discovery_job import DiscoveryJobService
from rq import Queue
from redis import Redis
import os as os_module

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        # Try PyPDF2 first
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            pass
        
        # Try pdfplumber
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except ImportError:
            pass
        
        # Fallback: try pypdf (newer name for PyPDF2)
        try:
            import pypdf
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            pass
        
        print(f"Warning: No PDF library found. Install PyPDF2, pdfplumber, or pypdf")
        return None
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {str(e)}")
        return None

def reset_and_discover(folder_path="/documents", collection_id=None):
    """Delete existing collection, load all documents, and start discovery"""
    app = create_app()
    with app.app_context():
        # Step 1: Delete existing collection if specified
        if collection_id:
            collection = Collection.query.get(collection_id)
            if collection:
                print(f"Deleting collection {collection_id}: {collection.name}")
                db.session.delete(collection)
                db.session.commit()
                print("Collection deleted successfully")
            else:
                print(f"Collection {collection_id} not found")
        else:
            # Delete all collections
            collections = Collection.query.all()
            for collection in collections:
                print(f"Deleting collection {collection.id}: {collection.name}")
                db.session.delete(collection)
            db.session.commit()
            print(f"Deleted {len(collections)} collection(s)")
        
        # Step 2: Create new collection
        collection = Collection(
            name='Documents Collection',
            description='Documents loaded from documents folder'
        )
        db.session.add(collection)
        db.session.commit()
        print(f"Created new collection {collection.id}: {collection.name}")
        
        # Step 3: Load documents from folder
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try the provided path as-is first (might be absolute)
        if os.path.isabs(folder_path):
            abs_folder_path = folder_path
        else:
            # Try relative to script, then relative to project root
            abs_folder_path = os.path.abspath(os.path.join(script_dir, folder_path))
            if not os.path.exists(abs_folder_path):
                # Try from project root (two levels up from scripts)
                project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
                abs_folder_path = os.path.abspath(os.path.join(project_root, folder_path))
        
        if not os.path.exists(abs_folder_path):
            print(f"Folder not found: {abs_folder_path}")
            return None
        
        print(f"Loading documents from: {abs_folder_path}")
        
        doc_service = DocumentService()
        loaded_count = 0
        failed_count = 0
        
        # Get all PDF files
        pdf_files = [f for f in os.listdir(abs_folder_path) if f.lower().endswith('.pdf')]
        print(f"Found {len(pdf_files)} PDF files")
        
        for filename in pdf_files:
            file_path = os.path.join(abs_folder_path, filename)
            try:
                # Extract text from PDF
                content = extract_text_from_pdf(file_path)
                if not content or len(content.strip()) < 10:
                    print(f"Skipping {filename}: No text extracted or too short")
                    failed_count += 1
                    continue
                
                # Remove null characters (PostgreSQL doesn't allow them)
                content = content.replace('\x00', '').replace('\0', '')
                
                # Use filename as title (remove .pdf extension)
                title = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
                
                # Add document
                doc = doc_service.add_document(
                    collection_id=collection.id,
                    content=content,
                    title=title,
                    file_path=file_path,
                    file_type='application/pdf'
                )
                loaded_count += 1
                if loaded_count % 10 == 0:
                    print(f"Loaded {loaded_count} documents...")
                    
            except Exception as e:
                print(f"Failed to load {filename}: {str(e)}")
                failed_count += 1
                continue
        
        print(f"\nDocument loading completed!")
        print(f"Successfully loaded: {loaded_count} documents")
        print(f"Failed: {failed_count} documents")
        
        # Step 4: Start discovery job
        print(f"\nStarting discovery job for collection {collection.id}...")
        redis_conn = Redis.from_url(os_module.getenv('REDIS_URL', 'redis://localhost:6379/0'))
        q = Queue(connection=redis_conn)
        
        from app.workers import run_discovery_job
        from app.models import DiscoveryJob, JobStatus
        
        # Create job record first
        job = DiscoveryJob(
            collection_id=collection.id,
            status=JobStatus.PENDING,
            rq_job_id=None
        )
        db.session.add(job)
        db.session.commit()
        
        try:
            rq_job = q.enqueue(run_discovery_job, collection.id, False, job.id)
            job.rq_job_id = rq_job.id
            db.session.commit()
            print(f"Discovery job started!")
            print(f"  Job ID: {job.id}")
            print(f"  RQ Job ID: {rq_job.id}")
            print(f"  Collection ID: {collection.id}")
            print(f"\nCheck status at: GET /collections/{collection.id}/discover/status")
        except Exception as e:
            print(f"Failed to start discovery job: {str(e)}")
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.session.commit()
            return None
        
        return collection.id

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Reset collection, load documents, and start discovery')
    parser.add_argument('--collection-id', type=int, help='Collection ID to delete (deletes all if not provided)')
    parser.add_argument('--folder', default='../documents', help='Path to documents folder')
    args = parser.parse_args()
    
    reset_and_discover(args.folder, args.collection_id)

