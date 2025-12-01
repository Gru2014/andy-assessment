# AI Assistance Disclosure

This document describes the AI tools, libraries, and assistance used in developing this project.

## AI Tools Used

- **OpenAI API**: Used for:
  - Text embeddings (text-embedding-3-small)
  - LLM completions (gpt-4o-mini) for topic naming, insights generation, and Q&A

- **Cursor AI Assistant**: Used for:
  - Code generation and scaffolding
  - Architecture design suggestions
  - Debugging assistance
  - Code review and improvements

## Libraries and Frameworks

### Backend
- Flask: Web framework
- SQLAlchemy: ORM
- OpenAI Python SDK: GenAI integration
- scikit-learn: Clustering algorithms
- RQ: Background job processing

### Frontend
- React: UI framework
- TypeScript: Type safety
- D3.js: Graph visualization
- Tailwind CSS: Styling
- Axios: HTTP client

## Code Generation

The following components were generated with AI assistance:
- Project structure and scaffolding
- Database models and migrations
- API route handlers
- Service layer implementations
- React components
- Docker configuration

All code was reviewed and adapted to meet the specific requirements of the challenge.

## Prompts Used

Key prompts used during development:
- "Create a Flask application with SQLAlchemy models for topic discovery"
- "Implement topic discovery service using clustering and GenAI"
- "Build a React component for interactive topic graph visualization"
- "Create background job system with Redis and RQ"
- "Implement incremental update logic for topic discovery"

## Attribution

- OpenAI API: https://platform.openai.com/
- Cursor AI: https://cursor.sh/
