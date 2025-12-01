# Frontend Environment Variables

This document explains how to configure environment variables for the frontend application.

## Environment Variables

The frontend uses Vite, which requires environment variables to be prefixed with `VITE_` to be exposed to the client-side code.

### Available Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:5000` | `http://localhost:5000` or `http://backend:5000` |
| `VITE_ENV` | Environment name | `development` | `development`, `production`, `staging` |
| `VITE_PORT` | Development server port | `5173` | `5173` |

## Setup

### Local Development

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set your values:
   ```env
   VITE_API_URL=http://localhost:5000
   VITE_ENV=development
   VITE_PORT=5173
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

### Docker Development

When running in Docker, the environment variables are passed as build arguments during the Docker build process.

1. Set variables in the root `.env` file or `docker-compose.yml`:
   ```env
   VITE_API_URL=http://backend:5000
   VITE_ENV=production
   ```

2. Rebuild the frontend container:
   ```bash
   docker-compose build frontend
   docker-compose up -d frontend
   ```

**Note:** In Docker, use `http://backend:5000` (the service name) instead of `localhost` because the frontend container needs to communicate with the backend container.

### Production Build

For production builds, set the environment variables before building:

```bash
export VITE_API_URL=https://api.example.com
export VITE_ENV=production
npm run build
```

Or use a `.env.production` file:
```env
VITE_API_URL=https://api.example.com
VITE_ENV=production
```

## How It Works

1. **Development**: Environment variables are read from `.env` files automatically by Vite
2. **Docker Build**: Variables are passed as build arguments (`ARG`) in the Dockerfile
3. **Runtime**: Variables are embedded into the JavaScript bundle at build time (not available at runtime)

## Important Notes

- ⚠️ **Build-time only**: Vite environment variables are embedded at build time, not runtime
- ⚠️ **Client-side exposure**: Only variables prefixed with `VITE_` are exposed to client code
- ⚠️ **No secrets**: Never put sensitive data (API keys, secrets) in `VITE_` variables as they will be exposed in the client bundle
- ✅ **API URLs**: Safe to use for API endpoints and configuration
- ✅ **Public config**: Use for non-sensitive configuration values

## Troubleshooting

### Variables not working?

1. Check the variable name starts with `VITE_`
2. Restart the dev server after changing `.env` files
3. Rebuild Docker containers after changing build args
4. Check browser console for the logged API URL (in development mode)

### Docker networking issues?

- Use service names (e.g., `backend`) instead of `localhost` in Docker
- Ensure containers are on the same Docker network
- Check `docker-compose.yml` dependencies

