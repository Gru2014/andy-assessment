"""Script to load documents from the documents folder"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Collection
from app.services.document_service import DocumentService

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
                for page in pdf.pages:
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

def load_documents_from_folder(collection_id=None, folder_path="/documents"):
    """Load documents from the documents folder"""
    app = create_app()
    with app.app_context():
        # Get or create collection
        if collection_id:
            collection = Collection.query.get(collection_id)
            if not collection:
                print(f"Collection {collection_id} not found")
                return
        else:
            # Create new collection
            collection = Collection(
                name='Documents Collection',
                description='Documents loaded from documents folder'
            )
            db.session.add(collection)
            db.session.commit()
            print(f"Created collection {collection.id}: {collection.name}")
        
        # Get absolute path - try multiple possible locations
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
            print(f"Tried paths:")
            print(f"  - {folder_path} (as provided)")
            if not os.path.isabs(folder_path):
                print(f"  - {os.path.abspath(os.path.join(script_dir, folder_path))}")
                print(f"  - {os.path.abspath(os.path.join(script_dir, '..', '..', folder_path))}")
            return
        
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
        
        print(f"\nCompleted!")
        print(f"Successfully loaded: {loaded_count} documents")
        print(f"Failed: {failed_count} documents")
        print(f"Collection ID: {collection.id}")
        return collection.id

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Load documents from folder')
    parser.add_argument('--collection-id', type=int, help='Collection ID to add documents to (creates new if not provided)')
    parser.add_argument('--folder', default='../documents', help='Path to documents folder')
    args = parser.parse_args()
    
    load_documents_from_folder(args.collection_id, args.folder)

