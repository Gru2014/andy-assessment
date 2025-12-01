# Frontend Commands

## Create Project Structure

```bash
# Create React + TypeScript project with Vite
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install

# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install additional dependencies
npm install d3 @types/d3 axios react-router-dom
```

## Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## Docker Commands

```bash
# Build image
docker build -t topic-discovery-frontend .

# Run container
docker run -p 3000:80 topic-discovery-frontend
```

