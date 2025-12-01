# Backend Commands

## Create Project Structure

```bash
# Create Flask app structure
mkdir -p app/{routes,services}
touch app/__init__.py app/models.py
touch app/routes/__init__.py
touch app/services/__init__.py

# Create migrations directory
mkdir -p migrations/versions

# Create tests directory
mkdir -p tests

# Create scripts directory
mkdir -p scripts
```

## Database Commands

```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## Development Commands

```bash
# Run development server
python run.py

# Run tests
pytest --cov=app

# Run tests with coverage report
pytest --cov=app --cov-report=html

# Start RQ worker
rq worker --url redis://localhost:6379/0
```

## Docker Commands

```bash
# Build image
docker build -t topic-discovery-backend .

# Run container
docker run -p 5000:5000 --env-file .env topic-discovery-backend
```

