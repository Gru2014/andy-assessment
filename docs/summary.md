# Technical Summary: Topic Discovery System

## Architecture and Data Flow

### System Architecture

The system follows a modular, layered architecture:

```
┌─────────────┐
│   Frontend  │ React + TypeScript + D3.js
│  (Port 3000)│
└──────┬──────┘
       │ HTTP/REST
┌──────▼──────┐
│   Backend   │ Flask API
│  (Port 5000)│
└──────┬──────┘
       │
   ┌───┴───┬──────────┬──────────┐
   │       │          │          │
┌──▼──┐ ┌──▼──┐  ┌───▼───┐  ┌───▼───┐
│ DB  │ │Redis│  │Worker │  │OpenAI │
│Postgres│ │     │  (RQ)  │  │  API  │
└─────┘ └─────┘  └───────┘  └───────┘
```

### Data Flow

1. **Document Ingestion**
   - Documents added via API
   - Content extracted and stored
   - Embeddings generated using OpenAI API
   - Embeddings stored in database

2. **Topic Discovery** (Background Job)
   - Embeddings retrieved from database
   - K-means clustering applied (adaptive cluster count)
   - Topic names generated via LLM from cluster documents
   - Document-topic assignments created with relevance scores

3. **Relationship Building**
   - Topic embeddings calculated (average of document embeddings)
   - Cosine similarity computed between topics
   - Relationships created if similarity > threshold (0.3)
   - Relationship types determined (STRONGLY_RELATED, RELATED, etc.)

4. **Insight Generation**
   - Top documents per topic selected
   - LLM generates: summary, themes, questions, concepts
   - Insights stored per topic

5. **Graph Construction**
   - Topics → nodes (with size, color, document count)
   - Relationships → edges (with weight, type)
   - JSON returned for frontend visualization

### Incremental Updates

When new documents are added:
- Only new documents are processed (embeddings generated)
- Existing topics are updated (not deleted/recreated)
- New clusters may be created if documents don't fit existing topics
- Relationships recalculated for affected topics
- Insights regenerated for updated topics

## Algorithm Choices and Justification

### Topic Discovery: K-means Clustering

**Why K-means?**
- Simple, efficient for moderate document counts
- Works well with high-dimensional embeddings
- Deterministic results (with fixed random seed)
- Fast enough for real-time updates

**Alternatives Considered:**
- **Hierarchical Clustering**: More accurate but O(n²) complexity
- **DBSCAN**: Better for varying cluster densities but requires tuning
- **LDA/BERTopic**: More semantic but slower and more complex

**Adaptive Cluster Count:**
- Formula: `max(2, min(10, n_docs // 3))`
- Balances granularity with computational cost
- Prevents over-clustering on small collections

### Topic Naming: LLM-based

**Why LLM?**
- Generates human-readable, meaningful topic names
- Understands context and themes
- Better than keyword extraction or centroid-based methods

**Prompt Design:**
- Uses sample documents from cluster (first 5, 500 chars each)
- Instructs concise naming (2-4 words)
- Fallback to generic names on failure

### Relationship Detection: Cosine Similarity

**Why Cosine Similarity?**
- Standard for embedding vectors
- Captures semantic similarity
- Normalized (0-1 range)
- Efficient computation

**Threshold:**
- 0.3 minimum similarity for relationships
- Prevents graph clutter
- Balances connectivity with noise

### Document Ranking: Relevance Score

**Why Centroid-based?**
- Topic centroid = average of document embeddings
- Relevance = cosine similarity to centroid
- Simple, interpretable
- Fast computation

## LLM/Embedding Usage

### Configuration

All LLM parameters are configurable via environment variables:
- `LLM_MODEL`: Model name (default: gpt-4o-mini)
- `EMBEDDING_MODEL`: Embedding model (default: text-embedding-3-small)
- `LLM_TEMPERATURE`: Creativity (default: 0.7)
- `LLM_MAX_TOKENS`: Response length (default: 2000)

### Abstraction Layer

`GenAIService` provides a clean abstraction:
- Single interface for all GenAI calls
- Easy model swapping
- Consistent error handling
- Retry logic (can be added)

### Caching Strategy

**Current:**
- Embeddings cached in database (DocumentEmbedding table)
- Prevents regeneration on incremental updates

**Future:**
- Cache LLM responses for similar prompts
- Use Redis for temporary caching
- Batch API calls where possible

### Cost Optimization

- Use cheaper models (gpt-4o-mini vs gpt-4)
- Limit content length for embeddings (8000 chars)
- Batch embedding requests where possible
- Reuse embeddings for incremental updates

## Challenges and Edge Cases

### 1. LLM Timeouts and Failures

**Handling:**
- Try-catch around all LLM calls
- Fallback to generic values (e.g., "Topic N")
- Graceful degradation (one failed insight doesn't break graph)
- Error messages logged and surfaced in UI

**Future:**
- Retry with exponential backoff
- Circuit breaker pattern
- Queue failed requests for retry

### 2. Empty or Small Collections

**Handling:**
- Minimum 2 clusters enforced
- Adaptive cluster count prevents over-clustering
- UI shows appropriate messages

### 3. Duplicate Topics

**Handling:**
- Cluster IDs used to identify existing topics
- Incremental updates merge into existing topics
- Unique constraints prevent duplicate assignments

### 4. Graph Rendering Performance

**Handling:**
- D3 force simulation for smooth rendering
- Limit initial node count (can paginate)
- Client-side filtering/search

### 5. Document Format Variations

**Handling:**
- Accept plain text content
- Truncate long documents (8000 chars for embeddings)
- Handle encoding issues gracefully

## Scaling to 1,000+ Documents

### Latency

**Current Bottlenecks:**
- Embedding generation: ~1-2s per document
- Clustering: O(n*k) where n=docs, k=clusters
- LLM calls: ~2-5s per topic

**Optimizations:**
1. **Batch Processing**
   - Batch embeddings (OpenAI supports up to 2048 items)
   - Parallel topic generation
   - Async processing pipeline

2. **Caching**
   - Cache embeddings aggressively
   - Cache LLM responses for similar clusters
   - Use Redis for hot data

3. **Incremental Processing**
   - Process new documents only
   - Update affected topics only
   - Background job for full recompute

4. **Database Optimization**
   - Index on collection_id, topic_id
   - Partition large tables
   - Use vector database (e.g., Pinecone, Weaviate) for embeddings

### Cost

**Current (100 docs):**
- Embeddings: ~$0.0001 per doc = $0.01
- LLM calls: ~$0.001 per topic = $0.01
- Total: ~$0.02 per discovery run

**At 1,000 docs:**
- Embeddings: ~$0.10
- LLM calls: ~$0.10 (assuming 30 topics)
- Total: ~$0.20 per run

**Optimizations:**
- Use cheaper embedding models
- Cache and reuse embeddings
- Batch API calls
- Use smaller LLM models for simple tasks

### Storage

**Current:**
- Embeddings: ~1536 floats × 4 bytes = 6KB per doc
- 1,000 docs = ~6MB embeddings
- Total DB size: ~50-100MB

**At 10,000+ docs:**
- Consider vector database (Pinecone, Weaviate)
- Separate storage for embeddings
- Archive old collections

### Architecture Changes

1. **Horizontal Scaling**
   - Multiple worker processes
   - Load balancer for API
   - Database read replicas

2. **Queue Management**
   - Priority queues (incremental vs full)
   - Job scheduling
   - Rate limiting

3. **Monitoring**
   - Job progress tracking
   - API latency metrics
   - Cost tracking

## Production Readiness

### Required Improvements

1. **Security**
   - [ ] Authentication and authorization
   - [ ] API rate limiting
   - [ ] Input validation and sanitization
   - [ ] Secrets management (e.g., Vault)

2. **Reliability**
   - [ ] Comprehensive error handling
   - [ ] Retry logic with backoff
   - [ ] Health checks and monitoring
   - [ ] Database backups

3. **Performance**
   - [ ] Database indexing optimization
   - [ ] API response caching
   - [ ] Connection pooling
   - [ ] Async processing improvements

4. **Observability**
   - [ ] Structured logging
   - [ ] Metrics collection (Prometheus)
   - [ ] Distributed tracing
   - [ ] Error tracking (Sentry)

5. **Testing**
   - [ ] Integration tests
   - [ ] End-to-end tests
   - [ ] Load testing
   - [ ] Mock external services

6. **Documentation**
   - [ ] API documentation (OpenAPI/Swagger)
   - [ ] Deployment guides
   - [ ] Runbooks
   - [ ] Architecture diagrams

### Deployment Recommendations

- **Container Orchestration**: Kubernetes or ECS
- **Database**: Managed PostgreSQL (RDS, Cloud SQL)
- **Cache**: Redis Cluster
- **CDN**: For frontend assets
- **CI/CD**: GitHub Actions or GitLab CI
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK stack or CloudWatch

## Conclusion

This prototype demonstrates a working topic discovery system with:
- Clean, modular architecture
- Background job processing
- Incremental updates
- Interactive visualization
- AI-powered insights

The system is designed to scale and can be productionized with the improvements outlined above.
