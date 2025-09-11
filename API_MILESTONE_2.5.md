# Milestone 2.5: Vector Embeddings & Semantic Search - Alexandria Priority Features

**Author**: Pixeltable Team  
**Date**: 2025-01-10  
**Estimated Duration**: 3 weeks  
**Dependencies**: Milestones 1 & 2 (basic API and data operations)

## Executive Summary
Milestone 2.5 accelerates development of vector embedding and semantic search capabilities specifically required by Alexandria, our flagship client with 10,000+ developers and 50,000+ daily searches. This targeted milestone enables Alexandria's migration from Python to JavaScript SDK while maintaining full functionality and performance.

---

## 1. Goals & Success Criteria

### Primary Goals
- [ ] **Goal 1**: Full vector embedding generation and management via API/SDK
- [ ] **Goal 2**: High-performance similarity search with < 200ms latency at p95
- [ ] **Goal 3**: Computed embedding columns with automatic generation
- [ ] **Goal 4**: Native Pixeltable query builder pattern in JavaScript
- [ ] **Goal 5**: Python SDK compatibility layer for smooth migration

### Success Metrics
- [ ] Semantic search returns same quality results as Python version
- [ ] Search latency < 200ms at p95 for 10k documents
- [ ] Embedding generation < 100ms for cached models
- [ ] Support 100+ concurrent users without degradation
- [ ] Zero breaking changes for Alexandria's existing data
- [ ] SDK type safety with full TypeScript support

---

## 2. Detailed Feature Specifications

### Feature 1: Vector Embeddings API (P0 - Critical)

#### API Endpoints
```yaml
POST /api/v1/embeddings/generate
  Request:
    Content-Type: application/json
    Body:
      text: string | string[]
      model: string  # e.g., "sentence-transformers/all-MiniLM-L6-v2"
      options:
        cache: boolean  # default: true
        normalize: boolean  # default: true
  Response:
    200 OK:
      embeddings: Float32Array | Float32Array[]
      model: string
      dimensions: number
      cached: boolean
    400 Bad Request:
      error: string

GET /api/v1/embeddings/models
  Response:
    200 OK:
      models: [
        {
          id: "sentence-transformers/all-MiniLM-L6-v2",
          dimensions: 384,
          type: "sentence",
          cached: true
        },
        {
          id: "openai/text-embedding-ada-002",
          dimensions: 1536,
          type: "document",
          cached: false
        }
      ]
```

#### SDK Interface
```typescript
// Core embedding functionality
interface EmbeddingClient {
  // Single text embedding
  generateEmbedding(
    text: string,
    model?: string
  ): Promise<Float32Array>;
  
  // Batch embedding for efficiency
  generateEmbeddings(
    texts: string[],
    model?: string
  ): Promise<Float32Array[]>;
  
  // List available models
  listModels(): Promise<EmbeddingModel[]>;
  
  // Model management
  preloadModel(modelId: string): Promise<void>;
  clearCache(): Promise<void>;
}

// Usage example matching Alexandria needs
const client = new PixeltableClient({ apiKey: process.env.PIXELTABLE_API_KEY });
const embedding = await client.embeddings.generate(
  "React component organization patterns",
  'sentence-transformers/all-MiniLM-L6-v2'
);
```

#### Implementation Notes
- **Caching Strategy**: LRU cache for frequently used embeddings
- **Model Loading**: Lazy loading with preload option for performance
- **Batch Optimization**: Process up to 100 texts in single request
- **Performance Target**: < 100ms for cached, < 500ms for uncached

### Feature 2: Similarity Search API (P0 - Critical)

#### API Endpoints
```yaml
POST /api/v1/tables/{table_name}/search/similarity
  Request:
    Body:
      query: string | Float32Array  # Text or pre-computed embedding
      column: string  # Embedding column to search
      limit: number  # Max results (default: 10)
      threshold: number  # Min similarity score (0-1)
      filters: WhereClause[]  # Additional SQL-like filters
      include_score: boolean  # Include similarity scores
  Response:
    200 OK:
      results: [
        {
          data: {...},  # Row data
          score: 0.95   # Similarity score if requested
        }
      ]
      query_embedding: Float32Array  # For debugging
      search_time_ms: number
```

#### SDK Interface
```typescript
interface SimilaritySearch {
  // Main search method
  search(
    tableName: string,
    query: string | Float32Array,
    options: {
      column: string;
      limit?: number;
      threshold?: number;
      filters?: WhereClause[];
      includeScore?: boolean;
    }
  ): Promise<SearchResult[]>;
  
  // Fluent API alternative
  similarity(query: string | Float32Array): SearchBuilder;
}

interface SearchBuilder {
  inColumn(column: string): SearchBuilder;
  where(condition: WhereClause): SearchBuilder;
  threshold(min: number): SearchBuilder;
  limit(n: number): SearchBuilder;
  execute(): Promise<SearchResult[]>;
}

// Alexandria use case example
const results = await client.tables.get('code_layouts')
  .similarity("How to organize React components")
  .inColumn('teaches_embedding')
  .where({ column: 'quality_score', operator: '>=', value: 7 })
  .where({ column: 'language', operator: '=', value: 'TypeScript' })
  .threshold(0.7)
  .limit(10)
  .execute();
```

### Feature 3: Computed Embedding Columns (P0 - Critical)

#### API Endpoints
```yaml
POST /api/v1/tables/{table_name}/columns/computed/embedding
  Request:
    Body:
      name: string  # Column name for embeddings
      source_column: string  # Text column to embed
      model: string  # Embedding model to use
      auto_update: boolean  # Update on source change
      cache: boolean  # Cache computed embeddings
  Response:
    201 Created:
      column_name: string
      type: "embedding"
      dimensions: number
      model: string
      source: string
```

#### SDK Interface
```typescript
interface ComputedColumns {
  createEmbeddingColumn(
    tableName: string,
    config: {
      name: string;
      sourceColumn: string;
      model: string;
      autoUpdate?: boolean;
      cache?: boolean;
    }
  ): Promise<ColumnInfo>;
  
  // List computed columns
  listComputedColumns(tableName: string): Promise<ComputedColumn[]>;
  
  // Refresh embeddings (if needed)
  refreshEmbeddings(
    tableName: string,
    columnName: string,
    where?: WhereClause
  ): Promise<RefreshResult>;
}

// Alexandria migration example
await client.computedColumns.createEmbeddingColumn('code_layouts', {
  name: 'teaches_embedding',
  sourceColumn: 'teaches',
  model: 'sentence-transformers/all-MiniLM-L6-v2',
  autoUpdate: true,
  cache: true
});
```

### Feature 4: Native Query Builder (P0 - Critical)

#### SDK Interface
```typescript
// Native Pixeltable object model in JavaScript
class PixeltableNative {
  // Initialize connection
  async init(config?: InitConfig): Promise<void>;
  
  // Get table with query builder
  getTable(name: string): Table;
  
  // Direct SQL-like operations
  sql(strings: TemplateStringsArray, ...values: any[]): Promise<any[]>;
}

interface Table {
  // Chainable query methods
  select(...columns: string[]): Query;
  where(condition: Condition | string, ...params: any[]): Query;
  orderBy(column: string, direction?: 'asc' | 'desc'): Query;
  limit(n: number): Query;
  offset(n: number): Query;
  
  // Similarity search integration
  similaritySearch(
    query: string | Float32Array,
    column: string
  ): Query;
  
  // Direct operations
  count(): Promise<number>;
  insert(data: Record<string, any>[]): Promise<InsertResult>;
  update(where: Condition, values: Record<string, any>): Promise<UpdateResult>;
  delete(where: Condition): Promise<DeleteResult>;
  
  // Column references for type safety
  columns: Record<string, Column>;
}

interface Query {
  // Continue chaining
  where(condition: Condition | string, ...params: any[]): Query;
  orderBy(column: string, direction?: 'asc' | 'desc'): Query;
  limit(n: number): Query;
  offset(n: number): Query;
  
  // Execute
  collect(): Promise<any[]>;
  first(): Promise<any | null>;
  stream(): AsyncIterable<any>;
  explain(): Promise<QueryPlan>;
}

// Alexandria's search implementation
const pxt = new PixeltableNative();
await pxt.init({ apiKey: process.env.PIXELTABLE_API_KEY });

const layouts = pxt.getTable('code_layouts');
const results = await layouts
  .select('repo_url', 'title', 'teaches', 'quality_score')
  .similaritySearch("React hooks best practices", 'teaches_embedding')
  .where('quality_score >= ?', 8)
  .where('language = ?', 'TypeScript')
  .orderBy('similarity_score', 'desc')
  .limit(10)
  .collect();
```

### Feature 5: Vector Index Management (P1 - High Priority)

#### API Endpoints
```yaml
POST /api/v1/tables/{table_name}/indexes/vector
  Request:
    Body:
      column: string  # Embedding column
      method: "ivfflat" | "hnsw"  # Index type
      parameters:
        lists?: number  # For IVFFlat
        m?: number  # For HNSW
        ef_construction?: number  # For HNSW
      metric: "cosine" | "euclidean" | "inner_product"
  Response:
    201 Created:
      index_name: string
      column: string
      method: string
      status: "building" | "ready"

GET /api/v1/tables/{table_name}/indexes
  Response:
    200 OK:
      indexes: [
        {
          name: string,
          type: "vector" | "btree" | "hash",
          column: string,
          status: string
        }
      ]
```

---

## 3. Technical Architecture

### System Design
```
┌─────────────┐    HTTPS/WSS    ┌─────────────┐     Query      ┌─────────────┐
│  JS SDK     │───────────────►│  API Server  │──────────────►│  Pixeltable  │
│  + Cache    │     (TLS)       │  (FastAPI)   │               │   Core       │
└─────────────┘                 └─────────────┘               └─────────────┘
       ▲                               │                              │
       │                               ▼                              ▼
       │                        ┌─────────────┐              ┌─────────────┐
       └────────────────────────│  Embedding   │              │   Vector     │
         Cached Embeddings      │   Service    │              │   Indexes    │
                               └─────────────┘              └─────────────┘
```

**Security Requirements:**
- All client-server communication uses TLS 1.3+
- API keys transmitted only over HTTPS
- WebSocket connections upgrade from HTTPS to WSS
- Certificate pinning recommended for mobile/desktop apps

### Sync Engine Architecture (In Development)

#### Why Skip Intermediate Caching
Rather than implementing temporary caching solutions, we're going directly to a proper sync engine architecture that will provide:
- **Instant responses** (<5ms) for all operations
- **Full offline capability** with automatic sync when reconnected  
- **Conflict-free** concurrent editing support
- **Reduced costs** through minimal server calls

#### Existing Sync Engine Solutions

**Option 1: Build on Replicache** (Recommended)
```typescript
// Replicache provides the sync infrastructure
import { Replicache } from 'replicache';

class PixeltableSyncEngine {
  private rep: Replicache;
  
  constructor() {
    this.rep = new Replicache({
      name: 'pixeltable',
      licenseKey: process.env.REPLICACHE_KEY,
      pushURL: '/api/replicache/push',
      pullURL: '/api/replicache/pull',
    });
  }
  
  // Instant local search with background sync
  async search(query: string): Promise<Results> {
    return await this.rep.query(async (tx) => {
      // Query local SQLite instantly
      return await tx.scan({ prefix: 'embeddings/' });
    });
  }
}
```
- **Pros**: Battle-tested (used by Reflect, Roam), handles conflicts, good docs
- **Cons**: Requires server-side integration, licensing costs

**Option 2: PowerSync for Vector Support**
```typescript  
// PowerSync with custom vector extension
import { PowerSyncDatabase } from '@journeyapps/powersync-sdk-web';

const db = new PowerSyncDatabase({
  schema: pixeltableSchema,
  database: { dbFilename: 'pixeltable.db' }
});
```
- **Pros**: SQLite-based, supports custom extensions, proven scale
- **Cons**: Need to add vector support ourselves

**Option 3: ElectricSQL** (New, Promising)
```typescript
// ElectricSQL - Postgres sync to SQLite
import { electrify } from 'electric-sql/wa-sqlite';

const electric = await electrify(conn, schema);
await electric.db.raw`
  SELECT * FROM layouts 
  WHERE embedding <-> ${queryVector} < 0.3
  ORDER BY embedding <-> ${queryVector}
`;
```
- **Pros**: Real Postgres with pgvector support, automatic sync
- **Cons**: Still in beta, may need optimization for embeddings

**Option 4: Custom Implementation**
Many companies build their own because:
- **Linear**: Custom sync for performance requirements
- **Figma**: Multiplayer editing needs custom CRDTs
- **Notion**: Complex permission model requires custom logic
- **Superhuman**: Email-specific optimizations

For Pixeltable's unique needs (embeddings, computed columns, media), a hybrid approach may be best:
```typescript
class PixeltableSyncEngine {
  // Use Replicache for sync infrastructure
  private sync: Replicache;
  // Use SQLite WASM for vector operations  
  private vectorDB: SQLiteVectorDB;
  // Custom embedding cache
  private embeddings: EmbeddingStore;
}
```

#### Current Status & User Communication

**For Users:**
```typescript
// Current API (available now)
const client = new PixeltableClient();
const results = await client.search(...);  // 150-200ms latency

// Coming Soon: Sync Engine (Q2 2025)
const client = new PixeltableClient({ 
  syncEngine: true  // Enable when available
});
const results = await client.search(...);  // <5ms latency
```

**Development Timeline:**
- **Now - Q1 2025**: API-based operations (current)
- **Q2 2025**: Beta sync engine for select customers
- **Q3 2025**: General availability

**Message to Alexandria:**
"While the sync engine is in development, the current API provides full functionality with 150-200ms search latency. The sync engine will be a seamless upgrade providing <5ms responses when it launches in Q2 2025."

### Data Flow for Alexandria Search
1. User enters search query in Alexandria UI
2. JS SDK checks local cache for embedding
3. If cached: Use immediately (<10ms)
4. If not cached: Request from API (~100ms)
5. Execute similarity search with filters
6. Vector index returns top-k results
7. Results enriched with metadata
8. Update local cache for future queries

### Performance Optimizations
```python
# Embedding cache implementation
class EmbeddingCache:
    def __init__(self, max_size: int = 10000):
        self.cache = LRUCache(max_size)
        self.model_cache = {}  # Keep models in memory
    
    async def get_embedding(self, text: str, model: str) -> np.ndarray:
        cache_key = f"{model}:{hash(text)}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        embedding = await self.generate(text, model)
        self.cache[cache_key] = embedding
        return embedding

# Connection pooling for SDK
class ConnectionPool:
    def __init__(self, min_size: int = 5, max_size: int = 20):
        self.connections = []
        self.available = asyncio.Queue()
        self.init_connections(min_size)
```

### File Structure
```
pixeltable/api/
├── v1/
│   ├── routers/
│   │   ├── embeddings.py       # New embedding endpoints
│   │   ├── search.py           # Similarity search endpoints
│   │   └── computed.py         # Computed column management
│   ├── services/
│   │   ├── embedding_service.py
│   │   ├── search_service.py
│   │   └── vector_index_service.py
│   └── models/
│       └── embedding_models.py

js-sdk/src/
├── native/
│   ├── query-builder.ts        # Native query builder
│   ├── table.ts               # Table class
│   └── expressions.ts         # Expression builder
├── embeddings/
│   ├── client.ts              # Embedding client
│   ├── cache.ts               # Client-side cache
│   └── models.ts              # Model definitions
└── search/
    ├── similarity.ts          # Similarity search
    └── vector-index.ts        # Index management
```

---

## 4. Implementation Plan

### Phase 1: Core Embedding Infrastructure (Days 1-5)
- [ ] Task 1.1: Set up embedding service with model management
- [ ] Task 1.2: Implement embedding generation endpoints
- [ ] Task 1.3: Add caching layer with LRU eviction
- [ ] Task 1.4: Create SDK embedding client
- [ ] Task 1.5: Write comprehensive tests for embeddings

### Phase 2: Similarity Search (Days 6-10)
- [ ] Task 2.1: Implement similarity search endpoint
- [ ] Task 2.2: Add filter support to search queries
- [ ] Task 2.3: Optimize vector operations for performance
- [ ] Task 2.4: Create SDK search builders (fluent & standard)
- [ ] Task 2.5: Performance testing with 10k+ documents

### Phase 3: Computed Columns & Native API (Days 11-15)
- [ ] Task 3.1: Implement computed embedding columns
- [ ] Task 3.2: Auto-update mechanism for source changes
- [ ] Task 3.3: Native query builder implementation
- [ ] Task 3.4: Type-safe column references
- [ ] Task 3.5: Python compatibility layer

### Phase 4: Optimization & Alexandria Integration (Days 16-21)
- [ ] Task 4.1: Vector index creation and management
- [ ] Task 4.2: Performance optimization for Alexandria scale
- [ ] Task 4.3: Migration utilities and scripts
- [ ] Task 4.4: Alexandria integration testing
- [ ] Task 4.5: Documentation and migration guide

---

## 5. Testing Strategy

### Performance Tests
```typescript
describe("Alexandria Performance Requirements", () => {
  test("semantic search < 200ms for 10k documents", async () => {
    const start = Date.now();
    const results = await client.search('code_layouts', 
      "React component patterns", {
        column: 'teaches_embedding',
        limit: 10
      });
    expect(Date.now() - start).toBeLessThan(200);
  });
  
  test("embedding generation < 100ms cached", async () => {
    // Warm cache
    await client.embeddings.generate("test", model);
    
    const start = Date.now();
    await client.embeddings.generate("test", model);
    expect(Date.now() - start).toBeLessThan(100);
  });
  
  test("handle 100 concurrent searches", async () => {
    const searches = Array(100).fill(null).map(() =>
      client.search('code_layouts', "test query", {...})
    );
    const results = await Promise.all(searches);
    expect(results).toHaveLength(100);
  });
});
```

### Migration Tests
```typescript
// Verify Python → JS compatibility
test("Python SDK pattern compatibility", async () => {
  // Python pattern
  // layouts.where(layouts.quality_score >= 8).collect()
  
  // JavaScript equivalent
  const results = await layouts
    .where('quality_score >= ?', 8)
    .collect();
  
  expect(results).toBeDefined();
});
```

---

## 6. Documentation Requirements

### API Documentation
- [ ] Complete OpenAPI spec for embedding endpoints
- [ ] Similarity search parameter documentation
- [ ] Performance tuning guide
- [ ] Model selection guide

### SDK Documentation
```markdown
# Alexandria Migration Guide

## Quick Start
```typescript
// 1. Install
npm install @pixeltable/sdk@next

// 2. Initialize with native API
const pxt = new PixeltableNative();
await pxt.init({ apiKey: process.env.PIXELTABLE_API_KEY });

// 3. Your existing Python patterns work!
const layouts = pxt.getTable('code_layouts');
const results = await layouts
  .select('*')
  .where('quality_score >= ?', 8)
  .collect();
```

## Migrating Search Queries
### Python (Current)
```python
results = layouts.order_by(
    layouts.teaches_embedding.similarity(query),
    asc=False
).limit(10).collect()
```

### JavaScript (New)
```typescript
const results = await layouts
  .similaritySearch(query, 'teaches_embedding')
  .limit(10)
  .collect();
```
```

### Alexandria-Specific Examples
- [ ] Complete search implementation
- [ ] Batch processing patterns
- [ ] Performance optimization tips
- [ ] Troubleshooting guide

---

## 7. Risk Assessment & Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Embedding model loading performance | High | High | Pre-load models, implement model pooling |
| Search latency > 200ms | Medium | High | Vector indexes, query optimization, caching |
| Memory usage with large embeddings | Medium | Medium | Streaming, pagination, memory limits |
| SDK type safety complexity | Low | Medium | Generated types, runtime validation |

### Alexandria-Specific Risks
- **Data Migration**: Provide scripts to verify data integrity
- **Performance Regression**: Extensive benchmarking before migration
- **API Differences**: Compatibility layer for gradual migration
- **Scale Testing**: Test with full 5000+ layouts dataset

---

## 8. Implementation Recommendations

### Sync Engine Implementation Strategy

#### Recommended Approach: Hybrid Architecture
Based on analysis of existing solutions and Pixeltable's unique requirements:

1. **Use Replicache for sync infrastructure** (don't reinvent the wheel)
   - Proven at scale with Reflect, Roam Research
   - Handles conflict resolution and offline state
   - Well-documented with good TypeScript support

2. **SQLite WASM for vector operations**
   - sqlite-vec extension for vector similarity
   - Runs entirely in browser/Node.js
   - Supports the SQL queries Alexandria needs

3. **Custom embedding layer**
   - Store embeddings in optimized format
   - Support multiple models simultaneously
   - Handle computed columns

#### Implementation Phases

**Phase 1: Foundation (Current - Milestone 2.5)**
- Standard API with 150-200ms latency
- Server-side caching for common queries
- Prepare data model for sync compatibility

**Phase 2: Sync Engine Beta (Q2 2025)**
- Deploy Replicache integration
- Implement SQLite WASM with vector support
- Beta test with Alexandria team
- Target: <10ms latency for cached data

**Phase 3: Production Release (Q3 2025)**
- Full offline support
- Conflict resolution for collaborative features
- Background sync optimization
- Target: <5ms latency for all operations

### Why Direct to Sync Engine?
- **Avoid technical debt**: No migration from intermediate solutions
- **Better user experience**: One major improvement vs. multiple small ones
- **Competitive advantage**: Match Linear/Figma performance immediately
- **Alexandria's scale**: 10,000+ users justifies proper solution

## 8. Rollout Strategy

### Alpha Testing with Alexandria (Week 3)
1. [ ] Deploy to Alexandria staging environment
2. [ ] Run parallel tests (Python vs JS)
3. [ ] Performance benchmarking
4. [ ] Identify and fix edge cases

### Beta Release (Week 4)
1. [ ] Limited rollout to Alexandria developers
2. [ ] Monitor performance metrics
3. [ ] Gather feedback on SDK ergonomics
4. [ ] Iterate based on real usage

### Production Readiness
- Performance metrics meet requirements
- Alexandria team sign-off
- Migration documentation complete
- Support channels established

---

## 9. Open Questions & Decisions Needed

### Technical Decisions
- [ ] **Q**: Should we support multiple embedding models simultaneously?
  - **Decision**: Yes - critical for Alexandria's future needs
  
- [ ] **Q**: Which sync engine approach to use?
  - **Decision**: Hybrid - Replicache + SQLite WASM + custom embeddings
  - **Rationale**: Leverages proven infrastructure while supporting vector operations
  - **Timeline**: Q2 2025 beta, Q3 2025 production

- [ ] **Q**: Support for custom embedding models?
  - **Decision**: Phase 2 - focus on standard models first
  
- [ ] **Q**: Build vs. buy for sync engine?
  - **Decision**: Buy core (Replicache), build vector-specific features
  - **Rationale**: Most companies build custom due to unique requirements, but Replicache provides solid foundation
  
- [ ] **Q**: How to communicate sync engine timeline to users?
  - **Decision**: Clear roadmap with Q2 2025 beta, API works fully now
  - **Message**: "Full functionality available today, 30x performance boost coming Q2"

### Product Decisions
- [ ] **Q**: Free tier embedding limits?
  - **Owner**: Product Team
  
- [ ] **Q**: Priority access for Alexandria?
  - **Owner**: Business Team

---

## 10. Resources & References

### Internal Documents
- [Alexandria Requirements Document](./PrincipleMD/alexandria/PIXELTABLE_JS_SDK_REQUIREMENTS.md)
- [SDK Adoption Strategy](./js-sdk/SDK_ADOPTION_STRATEGY.md)
- [Milestone 2 Specifications](./API_MILESTONE_2.md)

### External References
- [Sentence Transformers Documentation](https://www.sbert.net/)
- [Vector Index Benchmarks](https://ann-benchmarks.com/)
- [pgvector Performance Guide](https://github.com/pgvector/pgvector)

---

## Appendix A: Alexandria Integration Checklist

### Pre-Migration
- [ ] Export current Python table schemas
- [ ] Document all computed columns
- [ ] Benchmark current performance
- [ ] Identify custom UDFs

### Migration
- [ ] Set up JavaScript environment
- [ ] Install Pixeltable SDK
- [ ] Migrate table schemas
- [ ] Verify embedding generation
- [ ] Test search quality

### Post-Migration
- [ ] Performance validation
- [ ] User acceptance testing
- [ ] Monitor production metrics
- [ ] Document lessons learned

---

## Appendix B: Performance Benchmarks

### Target Metrics (from Alexandria requirements)
| Operation | Target | Current Python | Expected JS |
|-----------|--------|----------------|-------------|
| Single embedding | < 100ms | 95ms | 85ms |
| Batch embeddings (100) | < 1s | 950ms | 800ms |
| Similarity search (10k docs) | < 200ms | 180ms | 150ms |
| Filtered search | < 250ms | 220ms | 200ms |
| Concurrent searches (100) | < 500ms avg | 450ms | 400ms |

---

## Sign-off

- [ ] Engineering Lead: [Pending] - [Date]
- [ ] Alexandria Technical Lead: [Pending] - [Date]
- [ ] Product Manager: [Pending] - [Date]
- [ ] SDK Team Lead: [Pending] - [Date]

---

## Notes
This milestone represents a critical path for Alexandria's migration and serves as a proof point for Pixeltable's JavaScript SDK capabilities in production environments. Success here will unlock adoption by the 10,000+ developers in the Alexandria ecosystem.

Priority is given to features that directly enable Alexandria's use case while maintaining extensibility for future clients with similar needs.