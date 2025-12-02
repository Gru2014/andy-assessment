# Topic Discovery System

A prototype system that automatically discovers topics from document collections, builds interactive topic graphs, and provides AI-powered insights with Q&A capabilities.

## Features

- **Topic Discovery**: Automatically discovers main topics from document collections using GenAI
- **Interactive Topic Graph**: Visual graph showing topic relationships (nodes = topics, edges = relationships)
- **Topic Insights**: AI-generated summaries, themes, questions, and related concepts for each topic
- **Document Drill-down**: Ranked documents per topic with relevance scores and primary/secondary badges
- **Topic-scoped Q&A**: Ask questions about topics with inline citations to source documents
- **Incremental Updates**: Add new documents without full recomputation
- **Background Jobs**: Topic discovery runs as background jobs with progress tracking
- **Modular Architecture**: Clean separation between ingestion, storage, topic discovery, and Q&A

## Tech Stack

- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **Frontend**: HTMX, Tailwind CSS, D3.js (served directly from Flask)
- **ML/NLP**: OpenAI API (LLMs and Embeddings)
- **Background Jobs**: Redis, RQ (Redis Queue)
- **Tests**: pytest

## Quick Start

> 📖 **For detailed step-by-step instructions, see [BUILD_GUIDE.md](BUILD_GUIDE.md)**

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (or OpenAI-compatible API)

### Quick Setup

1. **Configure environment**

```bash
# Backend environment
cp backend/.env.example backend/.env
# Edit backend/.env and add your OPENAI_API_KEY

# Root .env (for Docker Compose) - optional
```

2. **Start the stack**

```bash
docker-compose up -d --build
```

3. **Initialize database**

```bash
docker-compose exec backend flask db upgrade
```

4. **Load documents (optional)**

```bash
docker-compose exec backend python scripts/load_documents_from_folder.py --folder /documents
```

5. **Access the application**

- Web UI: http://localhost:5000 (HTMX frontend served directly from Flask)
- Backend API: http://localhost:5000/api (JSON endpoints)
- Health check: http://localhost:5000/jobs/health

### Development Commands

```bash
make dev          # Build and start all services
make build        # Build Docker images
make up           # Start services
make down         # Stop services
make test         # Run tests with coverage
make db-upgrade   # Run database migrations
make load-data    # Load sample documents
make clean        # Clean up containers and volumes
```

## Project Structure

```
assessment/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── models.py            # Database models
│   │   ├── routes/              # API routes
│   │   │   ├── collections.py
│   │   │   ├── documents.py
│   │   │   ├── topics.py
│   │   │   └── jobs.py
│   │   └── services/            # Business logic
│   │       ├── genai_service.py
│   │       ├── topic_discovery.py
│   │       ├── relationship_service.py
│   │       ├── insight_service.py
│   │       ├── document_service.py
│   │       └── discovery_job.py
│   ├── tests/                   # Test suite
│   ├── scripts/                 # Utility scripts
│   ├── migrations/              # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── backend/
│   ├── app/
│   │   ├── templates/           # HTMX HTML templates
│   │   │   ├── base.html
│   │   │   ├── index.html
│   │   │   ├── graph.html
│   │   │   └── ...
└── docker-compose.yml
```

## API Endpoints

### Collections

- `GET /collections` - List all collections
- `POST /collections` - Create a new collection
- `GET /collections/<id>` - Get collection details
- `POST /collections/<id>/discover` - Start topic discovery (background job)
- `GET /collections/<id>/discover/status` - Get discovery job status

### Documents

- `POST /collections/<id>/documents` - Add documents to collection
- `GET /collections/<id>/documents` - List documents in collection
- `GET /collections/<id>/documents/<doc_id>` - Get document details

### Topics

- `GET /collections/<id>/topics/graph` - Get topic graph JSON
- `GET /topics/<id>` - Get topic drill-down view
- `POST /topics/<id>/qa` - Ask a question about a topic

### Jobs

- `GET /jobs/<id>` - Get job status
- `GET /jobs/health` - Health check

## Usage Workflow

1. **Access the web UI** - Open http://localhost:5000 in your browser
2. **Select a collection** - Choose from the dropdown
3. **Start discovery** - Click "Full Discovery" or "Incremental Update"
4. **View the graph** - Interactive topic graph appears (D3.js visualization)
5. **Click a topic node** - See topic details, documents, and insights
6. **Ask questions** - Use the Q&A feature with inline citations (clickable)
7. **Click citations** - Citations scroll to document previews
8. **Add more documents** - Use incremental update to update topics

## Testing

Run tests with coverage:

```bash
cd backend
pytest --cov=app --cov-report=html --cov-report=term
```

Test coverage target: >80% for core logic and key APIs.

## Configuration

Key environment variables (see `backend/.env.example`):

- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `OPENAI_BASE_URL` - API base URL (default: https://api.openai.com/v1)
- `LLM_MODEL` - LLM model name (default: gpt-4o-mini)
- `EMBEDDING_MODEL` - Embedding model (default: text-embedding-3-small)
- `LLM_TEMPERATURE` - LLM temperature (default: 0.7)
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

## Architecture

### Data Flow

1. **Document Ingestion**: Documents are added and embeddings are generated
2. **Topic Discovery**: Clustering on embeddings, topic name generation via LLM
3. **Relationship Building**: Calculate topic similarities and relationships
4. **Insight Generation**: Generate summaries, themes, questions, concepts per topic
5. **Graph Construction**: Build graph JSON for visualization

### Background Jobs

Topic discovery runs as background jobs using RQ (Redis Queue):
- Jobs are enqueued via API
- Worker processes execute discovery pipeline
- Job status and progress are tracked in database
- UI polls for status updates

### Incremental Updates

When new documents are added:
- Only new documents are processed
- Existing topics are updated (not recreated)
- New topics may be created if needed
- Relationships are recalculated

## Production Considerations

For production deployment:

1. **Security**: Use proper secrets management, enable HTTPS
2. **Scaling**: Consider horizontal scaling for workers, use connection pooling
3. **Caching**: Cache embeddings and insights to reduce API calls
4. **Monitoring**: Add logging, metrics, and error tracking
5. **Cost Optimization**: Batch API calls, use cheaper models where appropriate
6. **Database**: Use proper indexing, consider vector databases for embeddings

## License

Private and Confidential - Kalisa Technical Challenge

## AI Assistance Disclosure

See `docs/ai_assistance.md` for details on AI tools and assistance used in this project.
