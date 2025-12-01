# Complete Build Guide - Step by Step

This guide will walk you through building and running the Topic Discovery System from scratch.

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Codebase Overview](#codebase-overview)
3. [Prerequisites](#prerequisites-checklist)
4. [Step-by-Step Build Instructions](#step-1-navigate-to-project-directory)
5. [Troubleshooting](#troubleshooting-common-issues)

---

## High-Level Architecture

### System Overview

The Topic Discovery System is a full-stack application that automatically discovers topics from document collections using AI. Here's how it works:

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (React Frontend - Port 3000)                  │
│  • Topic Graph Visualization (D3.js)                             │
│  • Topic Details & Insights                                     │
│  • Document Drill-down                                          │
│  • Q&A with Citations                                            │
└───────────────────────┬─────────────────────────────────────────┘
                        │ HTTP/REST API
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                      BACKEND API                                 │
│                  (Flask - Port 5000)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Collections  │  │   Topics     │  │  Documents  │           │
│  │   Routes     │  │   Routes     │  │   Routes    │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐          │
│  │              Services Layer                       │          │
│  │  • DocumentService (ingestion)                     │          │
│  │  • TopicDiscoveryService (clustering + LLM)       │          │
│  │  • RelationshipService (graph building)            │          │
│  │  • InsightService (AI insights)                   │          │
│  │  • GenAIService (OpenAI abstraction)              │          │
│  └──────────────────────────────────────────────────┘          │
└───────┬──────────────────────────┬──────────────────────────────┘
        │                          │
        │                          │
┌───────▼──────────┐      ┌────────▼─────────────────────────────┐
│   PostgreSQL     │      │      Redis Queue                      │
│   (Database)     │      │  ┌────────────────────┐              │
│                   │      │  │  Background Worker │              │
│  • Collections   │      │  │  (RQ Worker)       │              │
│  • Documents     │      │  │                    │              │
│  • Topics        │      │  │  • Topic Discovery │              │
│  • Relationships │      │  │  • Graph Building │              │
│  • Insights      │      │  │  • Insight Gen     │              │
│  • Jobs          │      │  └────────────────────┘              │
└───────────────────┘      └──────────────────────────────────────┘
        │
        │
┌───────▼───────────────────────────────────────────────────────┐
│                    External Services                           │
│              OpenAI API (LLM + Embeddings)                     │
└────────────────────────────────────────────────────────────────┘
```

### Component Interactions

1. **Frontend → Backend**: React app makes HTTP requests to Flask API
2. **Backend → Database**: Flask uses SQLAlchemy ORM to store/retrieve data
3. **Backend → Redis**: Enqueues background jobs for topic discovery
4. **Worker → Database**: Worker processes jobs and updates database
5. **Worker → OpenAI**: Generates embeddings and LLM responses
6. **Backend → OpenAI**: Direct API calls for real-time operations

### Data Flow

**Document Ingestion Flow:**
```
PDF Files → DocumentService → Extract Text → Generate Embedding → Store in DB
```

**Topic Discovery Flow:**
```
Documents → Get Embeddings → K-means Clustering → Generate Topic Names (LLM) → 
Store Topics → Build Relationships → Generate Insights (LLM) → Return Graph
```

**Background Job Flow:**
```
API Request → Enqueue Job (Redis) → Worker Picks Up → Process Discovery → 
Update Database → Frontend Polls Status → Display Progress
```

---

## Codebase Overview

### Project Structure

```
assessment/
├── backend/                    # Python Flask Backend
│   ├── app/
│   │   ├── __init__.py        # Flask app factory & CORS setup
│   │   ├── models.py          # SQLAlchemy database models
│   │   ├── routes/            # API endpoints (REST)
│   │   │   ├── collections.py # Collection CRUD & discovery
│   │   │   ├── documents.py  # Document management
│   │   │   ├── topics.py      # Topic graph & Q&A
│   │   │   └── jobs.py        # Job status & health
│   │   ├── services/          # Business logic layer
│   │   │   ├── genai_service.py      # OpenAI API wrapper
│   │   │   ├── document_service.py   # Document ingestion
│   │   │   ├── topic_discovery.py    # Topic clustering & naming
│   │   │   ├── relationship_service.py # Topic relationships
│   │   │   ├── insight_service.py    # AI insights generation
│   │   │   └── discovery_job.py     # Background job orchestration
│   │   ├── workers.py        # RQ worker functions
│   │   └── migrations/       # Database migrations (Alembic)
│   ├── scripts/              # Utility scripts
│   │   └── load_documents_from_folder.py
│   ├── tests/                # Test suite
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Backend container
│   └── .env                  # Environment variables
│
├── frontend/                  # React TypeScript Frontend
│   ├── src/
│   │   ├── App.tsx           # Main application component
│   │   ├── api/
│   │   │   └── client.ts     # Axios API client
│   │   ├── components/
│   │   │   ├── TopicGraph.tsx      # D3.js graph visualization
│   │   │   ├── TopicDetail.tsx     # Topic drill-down view
│   │   │   ├── JobProgress.tsx     # Progress indicator
│   │   │   └── ui/                 # Reusable UI components
│   │   │       ├── Button.tsx
│   │   │       ├── Input.tsx
│   │   │       ├── Card.tsx
│   │   │       └── ...
│   │   └── index.css         # Tailwind CSS
│   ├── package.json          # Node dependencies
│   ├── vite.config.ts        # Vite configuration
│   ├── Dockerfile            # Frontend container
│   └── .env                  # Frontend environment variables
│
├── documents/                # PDF files to analyze (mounted volume)
├── docker-compose.yml        # Multi-container orchestration
├── Makefile                  # Common commands
├── BUILD_GUIDE.md           # This file
└── README.md                # Project overview
```

### Key Files Explained

#### Backend Core Files

**`backend/app/__init__.py`**
- Creates Flask application instance
- Configures CORS for frontend communication
- Sets up database connection
- Registers API blueprints

**`backend/app/models.py`**
- Defines database schema:
  - `Collection`: Document collections
  - `Document`: Individual documents with content
  - `DocumentEmbedding`: Vector embeddings for documents
  - `Topic`: Discovered topics
  - `DocumentTopic`: Many-to-many relationship (documents ↔ topics)
  - `TopicRelationship`: Topic-to-topic relationships
  - `TopicInsight`: AI-generated insights per topic
  - `DiscoveryJob`: Background job tracking

**`backend/app/services/genai_service.py`**
- Wraps OpenAI API calls
- Methods: `get_embedding()`, `chat_completion()`, `cosine_similarity()`
- Handles API errors and retries

**`backend/app/services/topic_discovery.py`**
- Core discovery logic:
  - `discover_topics()`: K-means clustering + LLM topic naming
  - `_generate_topic_name()`: Uses LLM to name topics
  - `calculate_relevance_scores()`: Computes document-topic relevance

**`backend/app/services/relationship_service.py`**
- `build_relationships()`: Calculates topic similarities
- Uses cosine similarity on topic embeddings
- Creates relationship types (STRONGLY_RELATED, RELATED, etc.)

**`backend/app/services/insight_service.py`**
- `generate_insights()`: Uses LLM to create:
  - Summary
  - Themes
  - Common questions
  - Related concepts

**`backend/app/routes/collections.py`**
- `POST /collections/{id}/discover`: Start discovery job
- `GET /collections/{id}/discover/status`: Get job progress
- `GET /collections`: List collections

**`backend/app/routes/topics.py`**
- `GET /collections/{id}/topics/graph`: Get graph JSON
- `GET /topics/{id}`: Get topic details with documents
- `POST /topics/{id}/qa`: Ask questions about topics

#### Frontend Core Files

**`frontend/src/App.tsx`**
- Main application component
- Manages state (collections, graph, selected topic)
- Handles API calls
- Renders UI layout

**`frontend/src/api/client.ts`**
- Axios instance with base URL from env
- API method definitions:
  - `collectionsApi`: Collection operations
  - `topicsApi`: Topic operations
  - `jobsApi`: Job status

**`frontend/src/components/TopicGraph.tsx`**
- D3.js force-directed graph
- Interactive nodes (clickable, draggable)
- Visual properties based on topic metrics
- Handles node clicks to show details

**`frontend/src/components/TopicDetail.tsx`**
- Displays topic information:
  - Insights (summary, themes, questions)
  - Documents ranked by relevance
  - Related topics
  - Q&A interface

**`frontend/src/components/ui/`**
- Reusable components:
  - `Button`: Styled buttons with variants
  - `Input`, `TextArea`, `Select`: Form inputs
  - `Card`: Container component
  - `Badge`: Labels/tags
  - `ProgressBar`: Progress indicators
  - `Heading`: Typography

### Service Architecture

**Document Service** (`document_service.py`)
- **Purpose**: Document ingestion
- **Key Methods**:
  - `add_document()`: Add single document + generate embedding
  - `add_documents_batch()`: Add multiple documents
- **Dependencies**: GenAIService (for embeddings)

**Topic Discovery Service** (`topic_discovery.py`)
- **Purpose**: Discover topics from documents
- **Key Methods**:
  - `discover_topics()`: Main discovery pipeline
  - `_generate_topic_name()`: LLM-based naming
  - `calculate_relevance_scores()`: Document-topic relevance
- **Algorithm**: K-means clustering on embeddings
- **Dependencies**: GenAIService, sklearn

**Relationship Service** (`relationship_service.py`)
- **Purpose**: Build topic graph relationships
- **Key Methods**:
  - `build_relationships()`: Calculate topic similarities
  - `_determine_relationship_type()`: Classify relationships
- **Algorithm**: Cosine similarity on topic embeddings
- **Dependencies**: GenAIService, numpy

**Insight Service** (`insight_service.py`)
- **Purpose**: Generate AI insights for topics
- **Key Methods**:
  - `generate_insights()`: Create insights for one topic
  - `generate_insights_batch()`: Batch processing
- **Dependencies**: GenAIService

**Discovery Job Service** (`discovery_job.py`)
- **Purpose**: Orchestrate background discovery pipeline
- **Key Methods**:
  - `run_discovery()`: Execute full pipeline with progress tracking
- **Pipeline Steps**:
  1. Discover topics (20% progress)
  2. Build relationships (50% progress)
  3. Generate insights (70% progress)
  4. Calculate relevance scores (90% progress)
  5. Complete (100% progress)

### Database Schema

**Collections Table**
- `id`, `name`, `description`, `created_at`

**Documents Table**
- `id`, `collection_id`, `title`, `content`, `file_path`, `file_type`, `created_at`

**Document Embeddings Table**
- `id`, `document_id`, `embedding` (vector), `model`

**Topics Table**
- `id`, `collection_id`, `name`, `cluster_id`, `document_count`, `size_score`, `color`

**Document Topics Table** (Many-to-Many)
- `id`, `document_id`, `topic_id`, `relevance_score`, `is_primary`

**Topic Relationships Table**
- `id`, `source_topic_id`, `target_topic_id`, `similarity_score`, `relationship_type`, `common_document_count`

**Topic Insights Table**
- `id`, `topic_id`, `summary`, `themes` (JSON), `common_questions` (JSON), `related_concepts` (JSON)

**Discovery Jobs Table**
- `id`, `collection_id`, `status`, `progress`, `current_step`, `error_message`, `rq_job_id`, `created_at`, `completed_at`

### API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/collections` | GET | List all collections |
| `/collections` | POST | Create collection |
| `/collections/{id}` | GET | Get collection details |
| `/collections/{id}/discover` | POST | Start discovery job |
| `/collections/{id}/discover/status` | GET | Get job status |
| `/collections/{id}/documents` | POST | Add documents |
| `/collections/{id}/documents` | GET | List documents |
| `/collections/{id}/topics/graph` | GET | Get topic graph JSON |
| `/topics/{id}` | GET | Get topic details |
| `/topics/{id}/qa` | POST | Ask question about topic |
| `/jobs/{id}` | GET | Get job by ID |
| `/jobs/health` | GET | Health check |

### Technology Stack Details

**Backend:**
- **Flask**: Web framework
- **SQLAlchemy**: ORM for database
- **PostgreSQL**: Relational database
- **Redis**: Job queue
- **RQ**: Redis Queue for background jobs
- **OpenAI API**: LLM and embeddings
- **scikit-learn**: K-means clustering
- **NumPy**: Numerical operations

**Frontend:**
- **React**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **D3.js**: Graph visualization
- **Axios**: HTTP client

**DevOps:**
- **Docker**: Containerization
- **Docker Compose**: Orchestration
- **Nginx**: Frontend web server

---

## File-by-File Build Order

This section provides the exact order to create/modify files, with dependencies clearly marked.

### Phase 1: Project Foundation

#### Step 1.1: Create Project Structure
**Files to create:**
```bash
mkdir -p backend/app/{routes,services}
mkdir -p backend/{tests,scripts,migrations}
mkdir -p frontend/src/{components/ui,api}
mkdir -p documents
```

**Dependencies:** None

---

### Phase 2: Backend Foundation

#### Step 2.1: `backend/requirements.txt`
**Purpose:** Python dependencies
**Dependencies:** None
**Create this file first** - defines all Python packages needed

**Key dependencies:**
- Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-CORS
- openai (>=1.40.0)
- redis, rq
- scikit-learn, numpy
- python-dotenv
- pypdf (for PDF extraction)

#### Step 2.2: `backend/app/__init__.py`
**Purpose:** Flask app factory, CORS setup, database initialization
**Dependencies:** None (but needs models.py next)
**What to include:**
- Flask app creation
- Database initialization
- CORS configuration
- Blueprint registration (routes)
- Error handlers

#### Step 2.3: `backend/app/models.py`
**Purpose:** Database models (SQLAlchemy)
**Dependencies:** `backend/app/__init__.py` (needs `db` from there)
**Order of models:**
1. `JobStatus` enum
2. `Collection` model
3. `Document` model
4. `DocumentEmbedding` model
5. `Topic` model
6. `DocumentTopic` model (many-to-many)
7. `TopicRelationship` model
8. `TopicInsight` model
9. `DiscoveryJob` model

**Why this order:** Models reference each other, so create base models first (Collection, Document) before junction tables.

#### Step 2.4: `backend/config.py` (if using separate config)
**Purpose:** Configuration settings
**Dependencies:** None
**What to include:**
- Database URL
- Redis URL
- OpenAI settings
- Environment-based configs

#### Step 2.5: `backend/.env.example` → `backend/.env`
**Purpose:** Environment variables template
**Dependencies:** None
**Variables needed:**
- `DATABASE_URL`
- `REDIS_URL`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL` (optional)
- `LLM_MODEL`, `EMBEDDING_MODEL`

**After creating:** Copy to `.env` and fill in values

---

### Phase 3: Core Services (Build in Order)

#### Step 3.1: `backend/app/services/genai_service.py`
**Purpose:** OpenAI API wrapper
**Dependencies:** None (but needs `.env` configured)
**What to include:**
- `GenAIService` class
- `get_embedding()` method
- `get_embeddings_batch()` method
- `chat_completion()` method
- `cosine_similarity()` method
- Lazy client initialization

**Why first:** All other services depend on this for embeddings/LLM calls.

#### Step 3.2: `backend/app/services/document_service.py`
**Purpose:** Document ingestion
**Dependencies:** `genai_service.py`, `models.py`
**What to include:**
- `DocumentService` class
- `add_document()` method (extract text, generate embedding, save)
- `add_documents_batch()` method
- PDF text extraction logic

**Why second:** Needed before topic discovery can work.

#### Step 3.3: `backend/app/services/topic_discovery.py`
**Purpose:** Topic clustering and naming
**Dependencies:** `genai_service.py`, `document_service.py`, `models.py`
**What to include:**
- `TopicDiscoveryService` class
- `discover_topics()` method (main pipeline)
- `_generate_topic_name()` method (LLM-based naming)
- `calculate_relevance_scores()` method
- K-means clustering logic
- Incremental update logic

**Why third:** Core discovery logic, but needs documents and embeddings first.

#### Step 3.4: `backend/app/services/relationship_service.py`
**Purpose:** Topic relationship building
**Dependencies:** `genai_service.py`, `topic_discovery.py`, `models.py`
**What to include:**
- `RelationshipService` class
- `build_relationships()` method
- `_determine_relationship_type()` method
- Cosine similarity calculations

**Why fourth:** Needs topics to exist first.

#### Step 3.5: `backend/app/services/insight_service.py`
**Purpose:** AI insight generation
**Dependencies:** `genai_service.py`, `topic_discovery.py`, `models.py`
**What to include:**
- `InsightService` class
- `generate_insights()` method (for one topic)
- `generate_insights_batch()` method
- LLM prompts for summaries, themes, questions

**Why fifth:** Needs topics and their documents first.

#### Step 3.6: `backend/app/services/discovery_job.py`
**Purpose:** Background job orchestration
**Dependencies:** All previous services
**What to include:**
- `DiscoveryJobService` class
- `run_discovery()` method (orchestrates full pipeline)
- Progress tracking
- Error handling

**Why last:** Orchestrates all other services.

---

### Phase 4: API Routes (Build in Order)

#### Step 4.1: `backend/app/routes/__init__.py`
**Purpose:** Register all route blueprints
**Dependencies:** All route files below
**What to include:**
- Import all blueprints
- Register with Flask app

#### Step 4.2: `backend/app/routes/jobs.py`
**Purpose:** Job status endpoints
**Dependencies:** `models.py`
**What to include:**
- `GET /jobs/{id}` - Get job by ID
- `GET /jobs/health` - Health check

**Why first:** Simplest routes, no service dependencies.

#### Step 4.3: `backend/app/routes/collections.py`
**Purpose:** Collection CRUD and discovery
**Dependencies:** `models.py`, `discovery_job.py`
**What to include:**
- `GET /collections` - List collections
- `POST /collections` - Create collection
- `GET /collections/{id}` - Get collection
- `POST /collections/{id}/discover` - Start discovery
- `GET /collections/{id}/discover/status` - Get status

**Why second:** Core collection operations.

#### Step 4.4: `backend/app/routes/documents.py`
**Purpose:** Document management
**Dependencies:** `models.py`, `document_service.py`
**What to include:**
- `POST /collections/{id}/documents` - Add documents
- `GET /collections/{id}/documents` - List documents

**Why third:** Document operations.

#### Step 4.5: `backend/app/routes/topics.py`
**Purpose:** Topic graph and Q&A
**Dependencies:** `models.py`, all services
**What to include:**
- `GET /collections/{id}/topics/graph` - Get graph JSON
- `GET /topics/{id}` - Get topic details
- `POST /topics/{id}/qa` - Ask question

**Why last:** Most complex, needs all services.

---

### Phase 5: Background Workers

#### Step 5.1: `backend/app/workers.py`
**Purpose:** RQ worker functions
**Dependencies:** `discovery_job.py`
**What to include:**
- `run_discovery_job()` function (decorated with `@rq.job`)
- Job status updates
- Error handling

---

### Phase 6: Database Migrations

#### Step 6.1: Initialize Flask-Migrate
**Commands:**
```bash
cd backend
flask db init  # Creates migrations/ directory
```

**Dependencies:** `models.py`, `app/__init__.py`

#### Step 6.2: Create Initial Migration
**Commands:**
```bash
flask db migrate -m "Initial migration"
```

**Dependencies:** All models defined

#### Step 6.3: Apply Migration
**Commands:**
```bash
flask db upgrade
```

**Dependencies:** Migration files created

---

### Phase 7: Utility Scripts

#### Step 7.1: `backend/scripts/load_documents_from_folder.py`
**Purpose:** Load PDFs from folder
**Dependencies:** `document_service.py`, `models.py`
**What to include:**
- PDF file discovery
- Text extraction
- Document creation via service
- Command-line arguments

---

### Phase 8: Frontend Foundation

#### Step 8.1: `frontend/package.json`
**Purpose:** Node.js dependencies
**Dependencies:** None
**Key dependencies:**
- react, react-dom
- typescript
- vite
- tailwindcss
- d3, @types/d3
- axios

#### Step 8.2: `frontend/vite.config.ts`
**Purpose:** Vite configuration
**Dependencies:** None
**What to include:**
- Environment variable prefix (`VITE_`)
- Proxy configuration for API
- Build settings

#### Step 8.3: `frontend/.env.example` → `frontend/.env`
**Purpose:** Frontend environment variables
**Dependencies:** None
**Variables:**
- `VITE_API_URL` (e.g., `http://localhost:5000`)

#### Step 8.4: `frontend/tailwind.config.js`
**Purpose:** Tailwind CSS configuration
**Dependencies:** None
**What to include:**
- Content paths (`./src/**/*.{js,ts,jsx,tsx}`)
- Theme customizations

#### Step 8.5: `frontend/src/index.css`
**Purpose:** Global styles
**Dependencies:** None
**What to include:**
- `@tailwind` directives
- Base styles

---

### Phase 9: Frontend API Client

#### Step 9.1: `frontend/src/api/client.ts`
**Purpose:** Axios API client
**Dependencies:** `frontend/.env` (for API URL)
**What to include:**
- Axios instance with base URL
- Request/response interceptors
- API method definitions:
  - `collectionsApi`
  - `topicsApi`
  - `jobsApi`

---

### Phase 10: Frontend UI Components (Build in Order)

#### Step 10.1: `frontend/src/components/ui/Button.tsx`
**Purpose:** Reusable button component
**Dependencies:** None
**What to include:**
- Button variants (primary, secondary, etc.)
- Size variants
- TypeScript props interface

#### Step 10.2: `frontend/src/components/ui/Input.tsx`
**Purpose:** Text input component
**Dependencies:** None
**What to include:**
- Input props (type, placeholder, value, onChange)
- Styling with Tailwind

#### Step 10.3: `frontend/src/components/ui/TextArea.tsx`
**Purpose:** Textarea component
**Dependencies:** None
**Similar to Input**

#### Step 10.4: `frontend/src/components/ui/Select.tsx`
**Purpose:** Dropdown select component
**Dependencies:** None

#### Step 10.5: `frontend/src/components/ui/Card.tsx`
**Purpose:** Card container component
**Dependencies:** None

#### Step 10.6: `frontend/src/components/ui/Badge.tsx`
**Purpose:** Badge/label component
**Dependencies:** None

#### Step 10.7: `frontend/src/components/ui/ProgressBar.tsx`
**Purpose:** Progress indicator
**Dependencies:** None

#### Step 10.8: `frontend/src/components/ui/Heading.tsx`
**Purpose:** Typography component
**Dependencies:** None

#### Step 10.9: `frontend/src/components/ui/index.ts`
**Purpose:** Export all UI components
**Dependencies:** All UI components above
**What to include:**
- Export statements for all components

---

### Phase 11: Frontend Feature Components

#### Step 11.1: `frontend/src/components/JobProgress.tsx`
**Purpose:** Job progress indicator
**Dependencies:** `api/client.ts`, `ui/ProgressBar.tsx`
**What to include:**
- Polling logic for job status
- Progress bar display
- Status messages

#### Step 11.2: `frontend/src/components/TopicGraph.tsx`
**Purpose:** D3.js graph visualization
**Dependencies:** `api/client.ts`, `d3` library
**What to include:**
- D3 force simulation setup
- Node rendering (topics)
- Edge rendering (relationships)
- Click handlers
- Zoom/pan functionality

**Why after JobProgress:** More complex, needs API working.

#### Step 11.3: `frontend/src/components/TopicDetail.tsx`
**Purpose:** Topic drill-down view
**Dependencies:** `api/client.ts`, all UI components
**What to include:**
- Topic insights display
- Document list with relevance scores
- Related topics
- Q&A interface

**Why last:** Most complex component.

---

### Phase 12: Frontend Main App

#### Step 12.1: `frontend/src/main.tsx`
**Purpose:** React entry point
**Dependencies:** `App.tsx`
**What to include:**
- ReactDOM render
- Import CSS

#### Step 12.2: `frontend/src/App.tsx`
**Purpose:** Main application component
**Dependencies:** All components, `api/client.ts`
**What to include:**
- State management (collections, graph, selected topic)
- API calls
- Component composition
- Layout structure

---

### Phase 13: Docker Configuration

#### Step 13.1: `backend/Dockerfile`
**Purpose:** Backend container
**Dependencies:** `requirements.txt`, all backend files
**What to include:**
- Python base image
- Install dependencies
- Copy application files
- Expose port 5000
- Run Flask app

#### Step 13.2: `frontend/Dockerfile`
**Purpose:** Frontend container
**Dependencies:** `package.json`, all frontend files
**What to include:**
- Node base image
- Install dependencies
- Build arguments for env vars
- Build production bundle
- Nginx to serve static files

#### Step 13.3: `docker-compose.yml`
**Purpose:** Multi-container orchestration
**Dependencies:** Both Dockerfiles, `.env` files
**What to include:**
- `db` service (PostgreSQL)
- `redis` service
- `backend` service
- `worker` service (RQ worker)
- `frontend` service
- Environment variables
- Volume mounts
- Network configuration

---

### Phase 14: Configuration Files

#### Step 14.1: `.env` (root)
**Purpose:** Docker Compose environment variables
**Dependencies:** None
**What to include:**
- `VITE_API_URL` (for frontend build)
- `VITE_ENV`

#### Step 14.2: `Makefile`
**Purpose:** Common commands
**Dependencies:** `docker-compose.yml`
**What to include:**
- `make up` - Start services
- `make down` - Stop services
- `make build` - Build images
- `make test` - Run tests
- `make db-upgrade` - Run migrations

---

### Phase 15: Documentation

#### Step 15.1: `README.md`
**Purpose:** Project overview
**Dependencies:** Project complete

#### Step 15.2: `BUILD_GUIDE.md` (this file)
**Purpose:** Detailed build instructions

---

## Build Order Summary

**Quick Reference - File Creation Order:**

1. **Foundation:**
   - Project structure (directories)
   - `backend/requirements.txt`
   - `frontend/package.json`

2. **Backend Core:**
   - `backend/app/__init__.py`
   - `backend/app/models.py`
   - `backend/config.py` (optional)
   - `backend/.env`

3. **Backend Services (in order):**
   - `backend/app/services/genai_service.py`
   - `backend/app/services/document_service.py`
   - `backend/app/services/topic_discovery.py`
   - `backend/app/services/relationship_service.py`
   - `backend/app/services/insight_service.py`
   - `backend/app/services/discovery_job.py`

4. **Backend Routes (in order):**
   - `backend/app/routes/jobs.py`
   - `backend/app/routes/collections.py`
   - `backend/app/routes/documents.py`
   - `backend/app/routes/topics.py`
   - `backend/app/routes/__init__.py`

5. **Backend Workers:**
   - `backend/app/workers.py`

6. **Database:**
   - Run `flask db init`
   - Run `flask db migrate`
   - Run `flask db upgrade`

7. **Frontend Foundation:**
   - `frontend/vite.config.ts`
   - `frontend/tailwind.config.js`
   - `frontend/src/index.css`
   - `frontend/.env`

8. **Frontend API:**
   - `frontend/src/api/client.ts`

9. **Frontend UI Components (any order):**
   - `frontend/src/components/ui/Button.tsx`
   - `frontend/src/components/ui/Input.tsx`
   - `frontend/src/components/ui/TextArea.tsx`
   - `frontend/src/components/ui/Select.tsx`
   - `frontend/src/components/ui/Card.tsx`
   - `frontend/src/components/ui/Badge.tsx`
   - `frontend/src/components/ui/ProgressBar.tsx`
   - `frontend/src/components/ui/Heading.tsx`
   - `frontend/src/components/ui/index.ts`

10. **Frontend Features:**
    - `frontend/src/components/JobProgress.tsx`
    - `frontend/src/components/TopicGraph.tsx`
    - `frontend/src/components/TopicDetail.tsx`

11. **Frontend Main:**
    - `frontend/src/App.tsx`
    - `frontend/src/main.tsx`

12. **Docker:**
    - `backend/Dockerfile`
    - `frontend/Dockerfile`
    - `docker-compose.yml`
    - Root `.env`

13. **Utilities:**
    - `backend/scripts/load_documents_from_folder.py`
    - `Makefile`

14. **Documentation:**
    - `README.md`
    - `BUILD_GUIDE.md`

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Docker** installed (version 20.10 or later)
- [ ] **Docker Compose** installed (version 2.0 or later)
- [ ] **Git** installed
- [ ] **OpenAI API Key** (or compatible API key)
- [ ] At least **4GB RAM** available for Docker
- [ ] At least **10GB free disk space**

### Verify Prerequisites

```bash
# Check Docker version
docker --version
docker-compose --version

# Check Docker is running
docker ps

# If you get "permission denied", add your user to docker group:
sudo usermod -aG docker $USER
newgrp docker
```

---

## Step 1: Navigate to Project Directory

```bash
cd /home/pony/Documents/assessment
pwd  # Should show: /home/pony/Documents/assessment
```

---

## Step 2: Configure Environment Variables

### 2.1 Backend Configuration

```bash
# Copy the example environment file
cp backend/.env.example backend/.env

# Edit the backend/.env file
nano backend/.env
# OR
gedit backend/.env
```

**Required configuration in `backend/.env`:**

```env
# REQUIRED: Your OpenAI API Key
OPENAI_API_KEY=sk-your-actual-api-key-here

# Optional: OpenAI-compatible API settings
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
SECRET_KEY=dev-secret-key-change-in-production

# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/topic_discovery

# Redis
REDIS_URL=redis://redis:6379/0
```

**⚠️ IMPORTANT:** Replace `sk-your-actual-api-key-here` with your real OpenAI API key!

### 2.2 Root Environment File (for Docker Compose)

```bash
# Check if root .env exists
cat .env
```

If it doesn't exist or is missing frontend variables, add:

```bash
# Add to root .env file
cat >> .env << 'EOF'

# Frontend Environment Variables
VITE_API_URL=http://backend:5000
VITE_ENV=development
EOF
```

---

## Step 3: Prepare Documents Folder

The system needs documents to analyze. Create the documents folder:

```bash
# Create documents directory if it doesn't exist
mkdir -p documents

# Verify it exists
ls -la documents/
```

**Optional:** Add some PDF files to analyze:
```bash
# Copy your PDF files to the documents folder
# cp /path/to/your/*.pdf documents/
```

---

## Step 4: Build Docker Images

Build all Docker containers:

```bash
# Build all services
docker-compose build

# This will take 5-10 minutes the first time
# You'll see output like:
# => [backend internal] load build context
# => [frontend internal] load build context
# => ...
```

**Expected output:**
- ✅ Backend image built successfully
- ✅ Frontend image built successfully
- ✅ Worker image built successfully

**If you see errors:**
- Check your internet connection (Docker needs to download base images)
- Ensure Docker has enough disk space: `docker system df`
- Check Docker logs: `docker-compose build --no-cache 2>&1 | tee build.log`

---

## Step 5: Start All Services

```bash
# Start all services in detached mode
docker-compose up -d

# Watch the logs to see services starting
docker-compose logs -f
```

**Wait for all services to be healthy:**
- Press `Ctrl+C` to stop watching logs
- Check service status: `docker-compose ps`

**Expected status:**
```
NAME                STATUS
assessment-db-1     Up (healthy)
assessment-redis-1  Up (healthy)
assessment-backend-1 Up
assessment-worker-1 Up
assessment-frontend-1 Up
```

---

## Step 6: Initialize Database

```bash
# Run database migrations
docker-compose exec backend flask db upgrade

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade -> c6e1f6ba155e, Initial migration
```

**If you see errors:**
```bash
# If migrations don't exist, create them
docker-compose exec backend flask db init
docker-compose exec backend flask db migrate -m "Initial migration"
docker-compose exec backend flask db upgrade
```

---

## Step 7: Load Documents (Optional but Recommended)

If you have documents in the `documents/` folder:

```bash
# Load documents from the documents folder
docker-compose exec backend python scripts/load_documents_from_folder.py --folder /documents

# This will:
# 1. Create a collection
# 2. Extract text from PDFs
# 3. Generate embeddings
# 4. Show progress
```

**Expected output:**
```
Loading documents from /documents...
Found 150 PDF files
Processing document 1/150...
...
Collection created: Documents Collection (ID: 7)
150 documents loaded successfully
```

---

## Step 8: Verify Services Are Running

### 8.1 Check Backend Health

```bash
# Test backend API
curl http://localhost:5000/jobs/health

# Expected response:
# {"status":"healthy","service":"topic-discovery-api"}
```

### 8.2 Check Frontend

Open your browser and navigate to:
```
http://localhost:3000
```

You should see the Topic Discovery System interface.

### 8.3 Check All Services

```bash
# View all running containers
docker-compose ps

# View logs for a specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs worker
```

---

## Step 9: Start Topic Discovery

### 9.1 Via Web UI

1. Open http://localhost:3000 in your browser
2. Select a collection from the dropdown
3. Click **"Full Discovery"** button
4. Watch the progress bar

### 9.2 Via API

```bash
# Start discovery for collection ID 1
curl -X POST http://localhost:5000/collections/1/discover \
  -H "Content-Type: application/json" \
  -d '{"incremental": false}'

# Check status
curl http://localhost:5000/collections/1/discover/status
```

---

## Step 10: Verify Everything Works

### 10.1 Check Collections

```bash
curl http://localhost:5000/collections
```

### 10.2 Check Topics

```bash
# Get topic graph for collection 1
curl http://localhost:5000/collections/1/topics/graph
```

### 10.3 Check Frontend

- Open http://localhost:3000
- You should see:
  - Collection selector
  - Topic graph (after discovery completes)
  - Topic details when clicking nodes
  - Document list

---

## Troubleshooting Common Issues

### Issue 1: Docker Permission Denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker ps
```

### Issue 2: Port Already in Use

```bash
# Check what's using the port
sudo lsof -i :5000
sudo lsof -i :3000

# Stop conflicting services or change ports in docker-compose.yml
```

### Issue 3: Database Connection Error

```bash
# Restart database
docker-compose restart db

# Wait for it to be healthy
docker-compose ps db

# Retry migration
docker-compose exec backend flask db upgrade
```

### Issue 4: OpenAI API Key Error

```bash
# Verify API key is set
docker-compose exec backend env | grep OPENAI_API_KEY

# If not set, check backend/.env file
cat backend/.env | grep OPENAI_API_KEY

# Rebuild backend if needed
docker-compose build backend
docker-compose up -d backend
```

### Issue 5: Frontend Not Loading

```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend

# Check if frontend container is running
docker-compose ps frontend
```

### Issue 6: Worker Not Processing Jobs

```bash
# Check worker logs
docker-compose logs worker

# Restart worker
docker-compose restart worker

# Check Redis connection
docker-compose exec worker redis-cli -h redis ping
```

---

## Quick Commands Reference

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Restart a service
docker-compose restart [service-name]

# Rebuild a service
docker-compose build [service-name]
docker-compose up -d [service-name]

# Access backend shell
docker-compose exec backend bash

# Access database
docker-compose exec db psql -U postgres -d topic_discovery

# Clean everything (WARNING: deletes data)
docker-compose down -v
docker system prune -a
```

---

## Verification Checklist

Before considering the build complete, verify:

- [ ] All Docker containers are running: `docker-compose ps`
- [ ] Backend health check passes: `curl http://localhost:5000/jobs/health`
- [ ] Frontend loads: http://localhost:3000
- [ ] Database migrations applied: `docker-compose exec backend flask db current`
- [ ] At least one collection exists: `curl http://localhost:5000/collections`
- [ ] Documents are loaded (if you added any)
- [ ] Topic discovery can be started from UI
- [ ] Progress bar shows in UI when discovery runs

---

## Next Steps After Build

1. **Load Documents**: Add PDF files to `documents/` folder and load them
2. **Start Discovery**: Click "Full Discovery" in the UI
3. **Explore Topics**: Click on topic nodes in the graph
4. **View Documents**: Click on documents in topic details
5. **Ask Questions**: Use the Q&A feature in topic details

---

## Support

If you encounter issues not covered here:

1. Check service logs: `docker-compose logs [service-name]`
2. Check Docker resources: `docker system df`
3. Verify environment variables are set correctly
4. Ensure all prerequisites are met
5. Try rebuilding: `docker-compose build --no-cache`

---

## Success Indicators

✅ **Build is successful when:**
- All containers show "Up" status
- Backend health endpoint returns 200
- Frontend loads without errors
- You can see the UI with collection selector
- Database migrations are applied
- No error messages in logs

Good luck with your assessment! 🚀
