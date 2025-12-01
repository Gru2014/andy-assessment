from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/topic_discovery')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    # Disable HTML error pages to ensure JSON errors with CORS
    app.config['PROPAGATE_EXCEPTIONS'] = True
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db, directory='migrations')
    # Configure CORS - allow all origins in development
    cors = CORS(app, origins=["http://localhost:5173", "http://localhost:3000"], supports_credentials=True)
    
    # Error handler to return JSON errors with CORS headers
    @app.errorhandler(Exception)
    def handle_error(e):
        # Don't handle errors in debug mode for Werkzeug debugger, but ensure CORS
        if app.debug and not request.is_json and 'application/json' not in request.headers.get('Accept', ''):
            # Let Flask's debug handler show HTML, but we'll add CORS in after_request
            raise
        
        status_code = 500
        if hasattr(e, 'code'):
            status_code = e.code
        elif hasattr(e, 'status_code'):
            status_code = e.status_code
        
        response = jsonify({'error': str(e)})
        response.status_code = status_code
        
        # Add CORS headers
        origin = request.headers.get('Origin')
        if origin in ["http://localhost:5173", "http://localhost:3000"]:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
    
    # Register blueprints
    from app.routes import collections, topics, documents, jobs
    app.register_blueprint(collections.bp)
    app.register_blueprint(topics.bp)
    app.register_blueprint(documents.bp)
    app.register_blueprint(jobs.bp)
    
    # Ensure CORS headers are added to all responses, including errors
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        allowed_origins = ["http://localhost:5173", "http://localhost:3000"]
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    
    return app

