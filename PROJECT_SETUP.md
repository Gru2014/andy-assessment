# Project Setup Commands

## Backend Project Creation

```bash
# Create backend directory structure
mkdir -p backend/app/{routes,services}
mkdir -p backend/{tests,scripts,migrations/versions}

# Initialize Python virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize Flask app
# (app/__init__.py, models.py, routes, services already created)

# Initialize database migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Frontend Project Creation

```bash
# Create React + TypeScript project with Vite
cd frontend
npm create vite@latest . -- --template react-ts

# Install base dependencies
npm install

# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install additional dependencies
npm install d3 @types/d3 axios react-router-dom

# Configure Tailwind (tailwind.config.js and postcss.config.js already created)
# Update src/index.css with @tailwind directives
```

## Full Stack Setup

```bash
# From project root
./setup.sh

# Or manually:
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Frontend
cd ../frontend
npm install
```

## Docker Setup

```bash
# Build and start all services
docker-compose up -d

# Or use Makefile
make up
```

## Development

```bash
# Backend (terminal 1)
cd backend
source venv/bin/activate
python run.py

# Worker (terminal 2)
cd backend
source venv/bin/activate
rq worker --url redis://localhost:6379/0

# Frontend (terminal 3)
cd frontend
npm run dev
```

