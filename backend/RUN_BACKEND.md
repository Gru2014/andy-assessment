# How to Run the Backend

## Option 1: Using Docker (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key

### Steps

1. **Create environment file**
```bash
cd backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

2. **Start all services (database, Redis, backend, worker)**
```bash
# From project root
docker-compose up -d

# Or use Makefile
make up
```

3. **Initialize database**
```bash
# From project root
make db-upgrade

# Or manually
docker-compose exec backend flask db upgrade
```

4. **Load documents from folder (optional)**
```bash
# Load PDFs from documents folder
docker-compose exec backend python scripts/load_documents_from_folder.py --folder /documents
```

5. **Check if backend is running**
```bash
curl http://localhost:5000/jobs/health
```

The backend will be available at: **http://localhost:5000**

---

## Option 2: Local Development (Without Docker)

### Prerequisites
- Python 3.11+
- PostgreSQL installed and running
- Redis installed and running
- OpenAI API key

### Steps

1. **Create virtual environment**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Create environment file**
```bash
cp .env.example .env
# Edit .env and set:
# - DATABASE_URL (e.g., postgresql://postgres:postgres@localhost:5432/topic_discovery)
# - REDIS_URL (e.g., redis://localhost:6379/0)
# - OPENAI_API_KEY (your API key)
```

4. **Set up database**
```bash
# Create database (PostgreSQL)
createdb topic_discovery  # Or use psql

# Initialize migrations
flask db init  # Only needed first time
flask db migrate -m "Initial migration"
flask db upgrade
```

5. **Start Redis** (in a separate terminal)
```bash
redis-server
```

6. **Start RQ worker** (in a separate terminal)
```bash
cd backend
source venv/bin/activate
rq worker --url redis://localhost:6379/0
```

7. **Run the backend server**
```bash
cd backend
source venv/bin/activate
python run.py
```

The backend will be available at: **http://localhost:5000**

---

## Quick Start Commands

### Using Docker (from project root)
```bash
make up              # Start all services
make db-upgrade      # Initialize database
make load-data       # Load sample data
make down            # Stop all services
```

### Local Development
```bash
# Terminal 1: Backend API
cd backend
source venv/bin/activate
python run.py

# Terminal 2: RQ Worker (for background jobs)
cd backend
source venv/bin/activate
rq worker --url redis://localhost:6379/0

# Terminal 3: Redis (if not running as service)
redis-server
```

---

## Verify Backend is Running

Test the health endpoint:
```bash
curl http://localhost:5000/jobs/health
```

Expected response:
```json
{"status": "healthy", "service": "topic-discovery-api"}
```

---

## Environment Variables

Required environment variables (in `backend/.env`):

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/topic_discovery

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# LLM Configuration (optional)
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# Application
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
```

---

## Troubleshooting

### Database connection error
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database exists: `psql -l`

### Redis connection error
- Ensure Redis is running: `redis-cli ping` (should return PONG)
- Check REDIS_URL in .env

### OpenAI API errors
- Verify OPENAI_API_KEY is set correctly
- Check API key has sufficient credits
- Verify OPENAI_BASE_URL is correct

### Port already in use
- Change port in `run.py` or use: `flask run --port 5001`

### Migration errors
- Try: `flask db stamp head` then `flask db upgrade`
- Or: `flask db downgrade -1` then `flask db upgrade`




