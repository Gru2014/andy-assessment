# Incremental Build Plan for Time Tracking

## Overview
This document provides a step-by-step plan for building the project incrementally, perfect for time tracking tools that capture screenshots.

## Build Strategy

### Principle: Build → Test → Document → Screenshot

For each step:
1. **Build** the feature
2. **Test** it works
3. **Document** what you did
4. **Screenshot** the result

---

## Session 1: Foundation (30-45 min)

### 1.1 Project Structure
```bash
mkdir -p assessment/{backend,frontend,docs}
cd assessment
git init
```

**Screenshot**: Directory tree
**Commit**: "Initial project structure"

### 1.2 Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-CORS python-dotenv
```

**Screenshot**: Virtual environment and installed packages
**Commit**: "Backend dependencies installed"

### 1.3 Frontend Setup
```bash
cd ../frontend
npm create vite@latest . -- --template react-ts
npm install
```

**Screenshot**: Frontend structure
**Commit**: "Frontend initialized"

---

## Session 2: Database Models (45-60 min)

### 2.1 Create Models File
- Create `backend/app/models.py`
- Add Collection, Document models first

**Screenshot**: Models code
**Test**: `python -c "from app.models import Collection; print('OK')"`
**Commit**: "Add Collection and Document models"

### 2.2 Add Topic Models
- Add Topic, DocumentTopic, TopicRelationship models

**Screenshot**: Updated models
**Commit**: "Add topic-related models"

### 2.3 Add Remaining Models
- Add TopicInsight, DiscoveryJob, DocumentEmbedding

**Screenshot**: Complete models.py
**Test**: Import all models successfully
**Commit**: "Complete database models"

### 2.4 Initialize Database
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

**Screenshot**: Migration files and database schema
**Commit**: "Database migrations initialized"

---

## Session 3: GenAI Service (30-45 min)

### 3.1 Create GenAI Service
- Create `backend/app/services/genai_service.py`
- Implement basic OpenAI client setup

**Screenshot**: Service code
**Test**: Test API connection (mock if no key)
**Commit**: "Add GenAI service foundation"

### 3.2 Add Embedding Methods
- Implement get_embedding(), get_embeddings_batch()

**Screenshot**: Embedding methods
**Commit**: "Add embedding methods"

### 3.3 Add LLM Methods
- Implement chat_completion()
- Add cosine_similarity helper

**Screenshot**: Complete GenAI service
**Test**: Generate test embedding
**Commit**: "Complete GenAI service"

---

## Session 4: Document Service (30 min)

### 4.1 Create Document Service
- Create `backend/app/services/document_service.py`
- Implement add_document()

**Screenshot**: Document service code
**Test**: Add a test document
**Commit**: "Add document service"

### 4.2 Add Batch Methods
- Implement add_documents_batch()
- Add embedding generation

**Screenshot**: Updated service
**Test**: Add multiple documents
**Commit**: "Add batch document processing"

---

## Session 5: Topic Discovery (60-90 min)

### 5.1 Create Discovery Service
- Create `backend/app/services/topic_discovery.py`
- Implement basic structure

**Screenshot**: Service structure
**Commit**: "Add topic discovery service"

### 5.2 Implement Clustering
- Add K-means clustering logic
- Process document embeddings

**Screenshot**: Clustering code
**Test**: Cluster sample documents
**Commit**: "Implement document clustering"

### 5.3 Add Topic Naming
- Implement _generate_topic_name() with LLM

**Screenshot**: Topic naming code
**Test**: Generate topic names
**Commit**: "Add LLM-based topic naming"

### 5.4 Complete Discovery
- Add document-topic assignments
- Calculate relevance scores

**Screenshot**: Complete discovery service
**Test**: Full discovery pipeline
**Commit**: "Complete topic discovery"

---

## Session 6: Relationships & Insights (45-60 min)

### 6.1 Relationship Service
- Create `backend/app/services/relationship_service.py`
- Implement build_relationships()

**Screenshot**: Relationship service
**Test**: Build relationships between topics
**Commit**: "Add relationship service"

### 6.2 Insight Service
- Create `backend/app/services/insight_service.py`
- Implement generate_insights()

**Screenshot**: Insight service
**Test**: Generate insights for a topic
**Commit**: "Add insight generation"

---

## Session 7: API Endpoints (60-90 min)

### 7.1 Collections API
- Create `backend/app/routes/collections.py`
- Implement basic CRUD

**Screenshot**: Collections routes
**Test**: Create/get collection via API
**Commit**: "Add collections API"

### 7.2 Documents API
- Create `backend/app/routes/documents.py`
- Implement add/list documents

**Screenshot**: Documents routes
**Test**: Add documents via API
**Commit**: "Add documents API"

### 7.3 Topics API
- Create `backend/app/routes/topics.py`
- Implement graph and topic endpoints

**Screenshot**: Topics routes
**Test**: Get topic graph JSON
**Commit**: "Add topics API"

### 7.4 Jobs & Health API
- Create `backend/app/routes/jobs.py`
- Add health endpoint

**Screenshot**: Jobs routes
**Test**: Health check endpoint
**Commit**: "Add jobs and health API"

---

## Session 8: Background Jobs (45-60 min)

### 8.1 Setup Redis & RQ
```bash
pip install redis rq
# Start Redis
```

**Screenshot**: Redis running, RQ installed
**Commit**: "Add Redis and RQ"

### 8.2 Discovery Job Service
- Create `backend/app/services/discovery_job.py`
- Implement run_discovery() with progress

**Screenshot**: Job service code
**Commit**: "Add discovery job service"

### 8.3 Worker Setup
- Create `backend/app/workers.py`
- Update routes to enqueue jobs

**Screenshot**: Worker code
**Test**: Start job and verify background execution
**Commit**: "Add background job worker"

### 8.4 Job Status Tracking
- Update models with progress fields
- Implement status updates

**Screenshot**: Job status in action
**Test**: Check job status via API
**Commit**: "Add job status tracking"

---

## Session 9: Frontend Foundation (45 min)

### 9.1 Setup Tailwind
```bash
cd frontend
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**Screenshot**: Tailwind config
**Commit**: "Setup Tailwind CSS"

### 9.2 API Client
- Create `src/api/client.ts`
- Define interfaces and API functions

**Screenshot**: API client code
**Test**: TypeScript compilation
**Commit**: "Add API client"

### 9.3 Basic App Structure
- Update `src/App.tsx`
- Add basic layout

**Screenshot**: Basic UI
**Commit**: "Add basic app structure"

---

## Session 10: Frontend Components (90-120 min)

### 10.1 Job Progress Component
- Create `src/components/JobProgress.tsx`

**Screenshot**: Progress component
**Test**: Display job status
**Commit**: "Add job progress component"

### 10.2 Topic Graph Component
```bash
npm install d3 @types/d3
```
- Create `src/components/TopicGraph.tsx`
- Implement D3 force graph

**Screenshot**: Graph component code
**Test**: Render graph with sample data
**Commit**: "Add topic graph component"

### 10.3 Topic Detail Component
- Create `src/components/TopicDetail.tsx`
- Add insights, documents, related topics

**Screenshot**: Topic detail component
**Test**: Click topic and show details
**Commit**: "Add topic detail component"

### 10.4 Q&A Feature
- Add Q&A section to TopicDetail
- Implement citations

**Screenshot**: Q&A with citations
**Test**: Ask question and see answer
**Commit**: "Add Q&A feature"

---

## Session 11: Integration (60 min)

### 11.1 Connect Frontend to Backend
- Update API calls
- Connect all components

**Screenshot**: Working integration
**Test**: Full flow end-to-end
**Commit**: "Connect frontend to backend"

### 11.2 Incremental Updates
- Implement incremental discovery
- Update UI for adding documents

**Screenshot**: Incremental update flow
**Test**: Add documents and verify update
**Commit**: "Add incremental updates"

### 11.3 Document Preview
- Add document preview
- Link citations

**Screenshot**: Document preview
**Test**: Click citation and see document
**Commit**: "Add document preview"

---

## Session 12: Testing (60-90 min)

### 12.1 Test Setup
- Create `backend/tests/conftest.py`
- Add fixtures

**Screenshot**: Test structure
**Commit**: "Add test fixtures"

### 12.2 Model Tests
- Create `backend/tests/test_models.py`

**Screenshot**: Model tests
**Test**: Run model tests
**Commit**: "Add model tests"

### 12.3 Service Tests
- Create `backend/tests/test_services.py`

**Screenshot**: Service tests
**Test**: Run service tests
**Commit**: "Add service tests"

### 12.4 API Tests
- Create `backend/tests/test_api.py`

**Screenshot**: API tests
**Test**: Run all tests with coverage
**Commit**: "Add API tests"

---

## Session 13: Docker (45 min)

### 13.1 Backend Dockerfile
- Create `backend/Dockerfile`

**Screenshot**: Dockerfile
**Test**: Build backend image
**Commit**: "Add backend Dockerfile"

### 13.2 Frontend Dockerfile
- Create `frontend/Dockerfile`
- Add nginx config

**Screenshot**: Frontend Dockerfile
**Test**: Build frontend image
**Commit**: "Add frontend Dockerfile"

### 13.3 Docker Compose
- Complete `docker-compose.yml`
- Add all services

**Screenshot**: docker-compose.yml
**Test**: `docker-compose up`
**Commit**: "Add docker-compose setup"

---

## Session 14: Documentation (60 min)

### 14.1 README
- Write comprehensive README.md

**Screenshot**: README
**Commit**: "Add README"

### 14.2 Technical Summary
- Write `docs/summary.md`

**Screenshot**: Summary document
**Commit**: "Add technical summary"

### 14.3 AI Assistance
- Write `docs/ai_assistance.md`

**Screenshot**: AI assistance doc
**Commit**: "Add AI assistance disclosure"

---

## Session 15: Polish (30-45 min)

### 15.1 Error Handling
- Add comprehensive error handling

**Screenshot**: Error handling
**Commit**: "Improve error handling"

### 15.2 UI Polish
- Improve styling
- Add loading states

**Screenshot**: Polished UI
**Commit**: "Polish UI"

### 15.3 Final Testing
- End-to-end testing
- Edge cases

**Screenshot**: Test results
**Commit**: "Final testing complete"

---

## Screenshot Best Practices

### What to Screenshot:

1. **Code Files** - Key implementations (not every file)
2. **Terminal Output** - Commands, test results, logs
3. **Browser/UI** - Working features, not just code
4. **Database** - Schema, sample data
5. **Test Results** - Coverage reports, passing tests

### When to Screenshot:

- ✅ After completing a logical feature
- ✅ After tests pass
- ✅ After integration works
- ✅ Before and after major changes
- ❌ Not every single line of code
- ❌ Not failed attempts (unless documenting issues)

### Screenshot Organization:

```
screenshots/
├── 01-foundation/
├── 02-models/
├── 03-services/
├── 04-api/
├── 05-jobs/
├── 06-frontend/
├── 07-integration/
├── 08-testing/
├── 09-docker/
└── 10-documentation/
```

---

## Time Estimates

- **Total**: ~15-20 hours
- **Backend**: ~8-10 hours
- **Frontend**: ~4-5 hours
- **Testing**: ~2-3 hours
- **Docker/Docs**: ~1-2 hours

---

## Quick Start Commands Reference

```bash
# Backend
cd backend
source venv/bin/activate
python run.py

# Worker
rq worker --url redis://localhost:6379/0

# Frontend
cd frontend
npm run dev

# Tests
pytest --cov=app

# Docker
docker-compose up -d
```






