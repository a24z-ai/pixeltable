# Pixeltable API Integration Testing Strategy

## Overview

This document outlines the integration testing approach for the Pixeltable REST API and JavaScript SDK. Our strategy emphasizes automated testing, consistency across environments, and rapid feedback loops for developers.

## Testing Philosophy

### Core Principles
1. **Test in Isolation**: Each test run should be independent and reproducible
2. **Fast Feedback**: Developers should get test results quickly during development
3. **Environment Parity**: Tests should run identically in local, Docker, and CI environments
4. **Comprehensive Coverage**: Test both happy paths and error scenarios
5. **Type Safety**: Leverage TypeScript for compile-time validation

## Testing Architecture

### Components Under Test

```
┌─────────────┐     HTTP      ┌─────────────┐     Python     ┌─────────────┐
│   JS SDK    │ ◄──────────► │  FastAPI    │ ◄──────────► │  Pixeltable │
│   (Bun)     │               │   Server    │               │    Core     │
└─────────────┘               └─────────────┘               └─────────────┘
                                     │
                                     ▼
                              ┌─────────────┐
                              │  PostgreSQL │
                              └─────────────┘
```

### Test Levels

1. **Unit Tests** (Not covered here)
   - SDK: TypeScript compilation and type checking
   - API: Python unit tests for individual endpoints

2. **Integration Tests** (Primary focus)
   - End-to-end API testing via SDK
   - Database state verification
   - Error handling and edge cases

3. **Contract Tests**
   - OpenAPI schema validation
   - Type generation verification
   - SDK-API compatibility

## Test Environments

### 1. Local Development Environment
**Purpose**: Rapid iteration during development
**Setup**: Minimal, uses local Python and Bun installations
**Usage**: `./scripts/test-api.sh`

```bash
# Prerequisites
uv pip install -e ".[api]"
cd js-sdk && bun install

# Run tests
./scripts/test-api.sh
```

**Pros**:
- Fastest feedback loop
- Easy debugging with local tools
- Direct access to logs

**Cons**:
- Requires local environment setup
- May have environment-specific issues

### 2. Docker Environment
**Purpose**: Consistent, reproducible testing
**Setup**: Docker Compose with all dependencies
**Usage**: `make -f Makefile.test test-docker`

```yaml
# docker-compose.test.yml structure
services:
  postgres    # Database
  api         # FastAPI server
  test-runner # Bun test execution
```

**Pros**:
- Completely isolated environment
- Matches production setup
- No local dependencies required

**Cons**:
- Slower than local testing
- Requires Docker installation

### 3. CI/CD Environment
**Purpose**: Automated validation on every change
**Setup**: GitHub Actions workflow
**Trigger**: Pull requests and merges to main

**Pros**:
- Automatic execution
- Consistent environment
- Blocks bad merges

**Cons**:
- Slower feedback than local
- Limited debugging capabilities

## Test Organization

### Directory Structure
```
tests/
├── integration/
│   ├── api.test.ts           # Core API tests
│   ├── tables.test.ts        # Table management tests
│   ├── data.test.ts          # Data operations tests (future)
│   └── auth.test.ts          # Authentication tests (future)
├── e2e/                      # End-to-end scenarios (future)
└── performance/              # Performance benchmarks (future)
```

### Test Categories

#### 1. Smoke Tests
Quick validation that the system is operational:
- Health check endpoints
- Basic table creation
- Simple CRUD operations

#### 2. Functional Tests
Comprehensive feature validation:
- All data types support
- Complex table operations
- Error handling scenarios
- Edge cases

#### 3. Negative Tests
Validation of error handling:
- Invalid inputs
- Non-existent resources
- Permission errors (when auth is added)
- Rate limiting (future)

## Test Data Management

### Strategies
1. **Test Prefixing**: All test tables use `test_` prefix
2. **Timestamp Suffixing**: Unique names with `Date.now()`
3. **Cleanup Hooks**: `afterAll()` removes test artifacts
4. **Database Isolation**: Each test run uses fresh database

### Example
```typescript
const testTableName = `test_table_${Date.now()}`;
// ... run tests
afterAll(() => client.dropTable(testTableName));
```

## Continuous Integration

### GitHub Actions Workflow
Triggers on:
- Pull requests (for changed files)
- Merges to main branch
- Manual workflow dispatch

### Pipeline Steps
1. **Build Phase**
   - Build Docker images
   - Compile TypeScript
   - Validate OpenAPI schema

2. **Test Phase**
   - Start services via Docker Compose
   - Run integration tests
   - Collect test results

3. **Cleanup Phase**
   - Tear down containers
   - Archive test artifacts
   - Report results

## Best Practices

### Writing Tests
1. **Use Descriptive Names**: Test names should explain what they validate
2. **Independent Tests**: Each test should be runnable in isolation
3. **Clean State**: Always clean up created resources
4. **Comprehensive Assertions**: Check both success and data correctness
5. **Error Messages**: Include context in test failures

### Example Test Structure
```typescript
describe("Feature: Table Management", () => {
  describe("when creating a table", () => {
    test("should create table with valid schema", async () => {
      // Arrange
      const tableName = `test_${Date.now()}`;
      const schema = { columns: { id: "int", name: "string" } };
      
      // Act
      const result = await client.createTable(tableName, schema);
      
      // Assert
      expect(result.message).toContain("success");
      const info = await client.getTable(tableName);
      expect(info.columns).toHaveLength(2);
      
      // Cleanup
      await client.dropTable(tableName);
    });
  });
});
```

## Performance Considerations

### Test Execution Time
- **Target**: Full suite under 5 minutes
- **Smoke tests**: Under 30 seconds
- **Parallel execution**: When possible
- **Docker layer caching**: For faster builds

### Resource Usage
- **Memory limits**: Set in Docker Compose
- **Connection pooling**: Reuse database connections
- **Test data size**: Keep minimal for speed

## Future Enhancements

### Near Term
1. **WebSocket Testing**: For real-time features
2. **Authentication Tests**: When auth is implemented
3. **Load Testing**: Basic performance validation
4. **SDK Language Support**: Python, Java clients

### Long Term
1. **Chaos Testing**: Network failures, timeouts
2. **Data Consistency Tests**: Multi-client scenarios
3. **Compatibility Testing**: Multiple Pixeltable versions
4. **Security Testing**: Input validation, SQL injection

## Troubleshooting

### Common Issues

#### API Server Won't Start
```bash
# Check if port 8000 is in use
lsof -i :8000
# Kill existing process if needed
pkill -f "python -m pixeltable.api"
```

#### Docker Tests Fail
```bash
# Clean up containers and volumes
docker-compose -f docker-compose.test.yml down -v
# Rebuild images
docker-compose -f docker-compose.test.yml build --no-cache
```

#### Type Generation Fails
```bash
# Ensure API server is running
python -m pixeltable.api
# Manually fetch OpenAPI schema
curl http://localhost:8000/openapi.json > openapi.json
```

## Metrics and Monitoring

### Key Metrics
- **Test Coverage**: Percentage of API endpoints tested
- **Test Duration**: Time to run full suite
- **Flakiness Rate**: Percentage of intermittent failures
- **Failure Rate**: Percentage of consistent failures

### Reporting
- **Local**: Console output with pass/fail
- **CI**: GitHub Actions annotations
- **Future**: Test dashboard with trends

## Conclusion

This integration testing strategy provides multiple levels of validation while maintaining developer productivity. The combination of local, Docker, and CI testing ensures code quality without sacrificing development speed.

For questions or improvements to this strategy, please open an issue or submit a pull request.