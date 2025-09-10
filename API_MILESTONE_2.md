# Pixeltable API & JS SDK - Milestone 2: Data Operations & Media Support

## Executive Summary
Building upon the foundation established in Milestone 1 (basic table management and REST API), Milestone 2 focuses on implementing core data operations, media handling capabilities, and enhanced SDK features to make Pixeltable a fully functional data platform via API.

## Timeline
- **Start Date**: January 15, 2025
- **Target Completion**: February 28, 2025
- **Duration**: 6 weeks

## Goals & Success Criteria

### Primary Goals
1. **Full CRUD Operations**: Complete data insertion, querying, updating, and deletion capabilities
2. **Media Support**: Handle images, video, and documents through the API
3. **Computed Columns**: Support for Pixeltable's unique computed column features
4. **Authentication & Security**: Basic auth and API key management
5. **Performance**: Handle datasets up to 100K rows efficiently

### Success Metrics
- [ ] API supports 100% of core Pixeltable operations
- [ ] SDK adoption by at least 3 internal projects
- [ ] 95% API test coverage
- [ ] Response times < 200ms for standard operations
- [ ] Documentation covers all new endpoints with examples

## Detailed Feature Specifications

### 1. Data Operations API (Priority: P0)

#### 1.1 Data Insertion
```
POST /api/v1/tables/{table_name}/rows
- Single row insertion
- Batch insertion (up to 1000 rows)
- Support for all Pixeltable data types
- Media upload via multipart/form-data
```

#### 1.2 Query Operations
```
GET /api/v1/tables/{table_name}/rows
- Pagination (limit/offset)
- Filtering (where clause support)
- Sorting (order_by)
- Column selection (select specific columns)
- Basic aggregations (count, sum, avg, min, max)
```

#### 1.3 Update Operations
```
PUT /api/v1/tables/{table_name}/rows/{row_id}
PATCH /api/v1/tables/{table_name}/rows
- Single row updates
- Batch updates with where clause
- Partial updates (PATCH)
```

#### 1.4 Delete Operations
```
DELETE /api/v1/tables/{table_name}/rows/{row_id}
DELETE /api/v1/tables/{table_name}/rows
- Single row deletion
- Batch deletion with where clause
- Soft delete option
```

### 2. Media Handling (Priority: P0)

#### 2.1 Upload Endpoints
```
POST /api/v1/media/upload
- Direct file upload
- URL-based media ingestion
- Supported formats: JPG, PNG, MP4, PDF, etc.
- Automatic format detection
```

#### 2.2 Media Processing
```
GET /api/v1/media/{media_id}/process
- Thumbnail generation
- Format conversion
- Metadata extraction
- Progress tracking for long operations
```

#### 2.3 Storage Integration
- Local filesystem support
- S3-compatible storage
- Configurable storage backends

### 3. Computed Columns & UDFs (Priority: P1)

#### 3.1 Computed Column Management
```
POST /api/v1/tables/{table_name}/computed-columns
- Define computed columns via API
- Python expression support
- Dependency tracking
```

#### 3.2 User-Defined Functions
```
POST /api/v1/udfs
GET /api/v1/udfs
- Register Python UDFs
- List available UDFs
- Execute UDFs on data
```

### 4. Authentication & Authorization (Priority: P0)

#### 4.1 API Key Management
```
POST /api/v1/auth/api-keys
- Generate API keys
- Revoke keys
- Key rotation
```

#### 4.2 Access Control
- Table-level permissions
- Operation-level permissions (read/write/delete)
- Rate limiting per API key

### 5. Enhanced JavaScript SDK (Priority: P0)

#### 5.1 New SDK Features
```typescript
// Data operations
await client.insertRows('table_name', data);
await client.query('table_name', { where: {...}, limit: 100 });
await client.updateRows('table_name', { where: {...}, set: {...} });
await client.deleteRows('table_name', { where: {...} });

// Media handling
await client.uploadMedia(file, { table: 'table_name', column: 'image' });
await client.processMedia(mediaId, { operation: 'thumbnail' });

// Computed columns
await client.addComputedColumn('table_name', {
  name: 'thumbnail',
  expression: 'resize(image, 128, 128)'
});
```

#### 5.2 TypeScript Improvements
- Full type inference for table schemas
- Async/await support throughout
- Streaming support for large datasets
- Progress callbacks for long operations

## Technical Architecture

### API Layer Changes
```
pixeltable/
├── api/
│   ├── v1/
│   │   ├── routers/
│   │   │   ├── tables.py (enhanced)
│   │   │   ├── data.py (new)
│   │   │   ├── media.py (new)
│   │   │   ├── computed.py (new)
│   │   │   └── auth.py (new)
│   │   ├── models/
│   │   │   ├── requests.py
│   │   │   └── responses.py
│   │   └── services/
│   │       ├── data_service.py
│   │       ├── media_service.py
│   │       └── auth_service.py
│   └── middleware/
│       ├── authentication.py
│       └── rate_limiting.py
```

### Database Schema
```sql
-- API Keys table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY,
    key_hash VARCHAR(256) UNIQUE,
    name VARCHAR(100),
    permissions JSONB,
    created_at TIMESTAMP,
    last_used TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE
);

-- API Usage tracking
CREATE TABLE api_usage (
    id BIGSERIAL PRIMARY KEY,
    api_key_id UUID REFERENCES api_keys(id),
    endpoint VARCHAR(200),
    method VARCHAR(10),
    status_code INT,
    response_time_ms INT,
    timestamp TIMESTAMP
);
```

## Implementation Plan

### Phase 1: Core Data Operations (Weeks 1-2)
- [ ] Implement insertion endpoints
- [ ] Implement query endpoints with filtering
- [ ] Implement update/delete operations
- [ ] Add pagination and sorting
- [ ] Update SDK with data operations

### Phase 2: Media Support (Weeks 3-4)
- [ ] File upload infrastructure
- [ ] Media processing pipeline
- [ ] Storage backend abstraction
- [ ] SDK media handling methods
- [ ] Progress tracking for long operations

### Phase 3: Advanced Features (Week 5)
- [ ] Computed column API
- [ ] UDF registration and execution
- [ ] Batch operations optimization
- [ ] Streaming support

### Phase 4: Security & Polish (Week 6)
- [ ] API key generation and management
- [ ] Authentication middleware
- [ ] Rate limiting
- [ ] Performance optimization
- [ ] Final testing and documentation

## Testing Strategy

### Unit Testing
- Service layer tests (90% coverage)
- Router tests with mocked dependencies
- SDK unit tests

### Integration Testing
- End-to-end API tests
- Media upload/processing tests
- Authentication flow tests
- Rate limiting tests

### Performance Testing
- Load testing with 1000 concurrent requests
- Large dataset operations (100K+ rows)
- Media processing benchmarks
- Memory usage profiling

### Test Data
- Synthetic datasets for various data types
- Sample media files (images, videos, documents)
- Edge cases and error scenarios

## Documentation Requirements

### API Documentation
- OpenAPI 3.0 specification
- Interactive Swagger UI
- Authentication guide
- Rate limiting documentation
- Error code reference

### SDK Documentation
- TypeScript API reference
- Getting started guide
- Code examples for all operations
- Migration guide from Milestone 1

### Tutorials
- "Building a Media Gallery with Pixeltable API"
- "Data Processing Pipeline Example"
- "Implementing Custom Computed Columns"

## Risk Assessment & Mitigation

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Media processing performance | High | Medium | Implement async processing with job queues |
| API key security | High | Low | Use industry-standard hashing, rotate keys regularly |
| Large dataset handling | Medium | Medium | Implement pagination, streaming, and caching |
| SDK type generation complexity | Low | Medium | Maintain manual overrides for complex types |

### Dependencies
- FastAPI security extensions
- Media processing libraries (Pillow, ffmpeg)
- Storage backends (boto3 for S3)
- Authentication libraries

## Rollout Strategy

### Beta Testing (Week 5)
1. Internal team testing
2. Select partner access
3. Performance monitoring
4. Bug fixes and optimizations

### Production Release (Week 6)
1. Gradual rollout with feature flags
2. Monitor API usage and performance
3. Gather user feedback
4. Iterate based on usage patterns

## Resource Requirements

### Team
- 2 Backend Engineers (Python/FastAPI)
- 1 Frontend Engineer (TypeScript/SDK)
- 1 DevOps Engineer (deployment/monitoring)
- 1 Technical Writer (documentation)

### Infrastructure
- Development API servers
- Staging environment
- CI/CD pipeline enhancements
- Monitoring and logging infrastructure

## Success Metrics Review

### Week 6 Checkpoint
- [ ] All P0 features implemented and tested
- [ ] API documentation complete
- [ ] SDK published to npm registry
- [ ] Performance benchmarks met
- [ ] Security audit passed

## Open Questions & Decisions

1. **Q**: Should we support GraphQL in addition to REST?
   - **Decision**: Defer to Milestone 3

2. **Q**: How to handle very large file uploads (>1GB)?
   - **Decision**: Implement chunked upload in Milestone 3

3. **Q**: Should computed columns support external API calls?
   - **Decision**: Security review needed, defer decision

## Migration from Milestone 1

### Breaking Changes
- None planned - full backward compatibility

### Deprecations
- `/api/v1/tables/{name}/info` → `/api/v1/tables/{name}` (consolidated)

### SDK Migration
```typescript
// Old (Milestone 1)
const tables = await client.listTables();

// New (Milestone 2) - backward compatible
const tables = await client.listTables();
// Plus new features
const data = await client.query('my_table', { limit: 10 });
```

## Resources & References

### Internal
- [Pixeltable Core Documentation](https://github.com/pixeltable/pixeltable)
- [API Design Guidelines](internal-link)
- [Security Best Practices](internal-link)

### External
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## Appendices

### A. API Endpoint Summary
Full list of 25+ new endpoints with request/response schemas

### B. Error Codes
Comprehensive error code reference (4xx, 5xx)

### C. Performance Benchmarks
Baseline measurements and target metrics

---

## Sign-off

### Stakeholders
- [ ] Engineering Lead
- [ ] Product Manager
- [ ] Security Team
- [ ] DevOps Team

### Review Date
- Technical Review: January 10, 2025
- Final Approval: January 14, 2025

---

*This document is a living specification and will be updated as implementation progresses.*