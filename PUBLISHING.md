# Publishing Guide for Pixeltable API & SDK

This document outlines the process for publishing the Pixeltable API server and JavaScript SDK packages.

## Overview

We maintain two published packages:
1. **Python Package**: `pixeltable` on PyPI (includes optional API server)
2. **JavaScript Package**: `@a24z/pixeltable-sdk` on npm

## Pre-Publishing Checklist

Before publishing either package:

- [ ] All tests pass locally
- [ ] Documentation is up to date
- [ ] Version numbers are bumped appropriately
- [ ] CHANGELOG is updated (if applicable)
- [ ] Pre-commit hooks pass
- [ ] CI/CD pipeline is green

## JavaScript SDK Publishing (`@a24z/pixeltable-sdk`)

### Prerequisites

1. **npm Account**: Must be logged in with publish access to `@a24z` org
   ```bash
   npm login
   npm whoami  # Verify you're logged in
   ```

2. **Bun Installed**: Required for building
   ```bash
   curl -fsSL https://bun.sh/install | bash
   ```

### Publishing Process

#### Automated Publishing

Use the provided script for interactive publishing:

```bash
./scripts/publish-npm.sh
```

This script will:
1. Prompt for version bump (patch/minor/major)
2. Run linting and tests
3. Build the package
4. Perform a dry run
5. Publish to npm with confirmation

#### Manual Publishing

If you prefer manual control:

```bash
cd js-sdk

# 1. Update version
npm version patch  # or minor/major

# 2. Run checks
bun run lint
bun test

# 3. Build
bun run build

# 4. Dry run
npm publish --dry-run

# 5. Publish
npm publish

# 6. Tag the release
git tag js-sdk-v0.1.0  # Use actual version
git push --tags
```

### Configuration Files

- `js-sdk/package.json`: Package configuration
  - Name: `@a24z/pixeltable-sdk`
  - Entry points: CommonJS and ESM
  - TypeScript definitions included
  - Pre-publish hooks for quality assurance

- `js-sdk/tsconfig.json`: TypeScript configuration
  - Strict type checking enabled
  - Bun-specific settings

### Build Output

The build process creates:
- `dist/index.js` - CommonJS bundle
- `dist/index.mjs` - ESM bundle  
- `dist/index.d.ts` - TypeScript definitions

## Python API Publishing (Part of `pixeltable`)

### Overview

The API server is distributed as an optional dependency of the main `pixeltable` package on PyPI.

### Installation by Users

Users install the API server with:
```bash
pip install pixeltable[api]
```

This installs:
- Core pixeltable package
- FastAPI and Uvicorn dependencies
- API server module at `pixeltable.api`

### Publishing Process

The API server is published as part of the main Pixeltable package:

1. **Update pyproject.toml**:
   ```toml
   [project.optional-dependencies]
   api = [
       "fastapi>=0.115.0",
       "uvicorn[standard]>=0.32.0",
   ]
   ```

2. **Build and Publish** (handled by main project):
   ```bash
   # Using uv (project's package manager)
   uv build
   uv publish
   
   # Or using standard tools
   python -m build
   python -m twine upload dist/*
   ```

### Running the Published API

After installation, users can run:
```bash
python -m pixeltable.api
```

This starts the FastAPI server on `http://localhost:8000`

## Version Management

### Semantic Versioning

Both packages follow semantic versioning:
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Version Synchronization

While not strictly required, consider keeping versions aligned:
- API server version follows main Pixeltable version
- JS SDK can version independently but should note compatible API versions

Example compatibility matrix:
| Pixeltable (API) | JS SDK | Notes |
|-----------------|--------|-------|
| 0.2.x | 0.1.x | Initial release |
| 0.3.x | 0.2.x | Added new endpoints |
| 1.0.x | 1.0.x | Stable release |

## Pre-commit Hooks

### Setup

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

### Configuration

The `.pre-commit-config.yaml` includes:
- Python: Ruff formatting and linting
- TypeScript: Type checking and tests
- General: Trailing whitespace, file size limits

### Running Manually

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files
pre-commit run
```

## CI/CD Integration

### GitHub Actions

The `.github/workflows/api-integration-tests.yml` workflow:
- Triggers on PRs affecting API or SDK
- Runs integration tests in Docker
- Validates TypeScript compilation
- Checks package builds

### Release Automation (Future)

Consider automating releases with:
```yaml
name: Release
on:
  push:
    tags:
      - 'js-sdk-v*'
jobs:
  publish-npm:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - run: cd js-sdk && bun install
      - run: cd js-sdk && bun run build
      - run: cd js-sdk && npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Troubleshooting

### npm Publishing Issues

**Authentication Error**:
```bash
npm login
npm whoami  # Verify logged in
```

**Permission Error**:
Ensure you're a member of the `@a24z` organization with publish rights.

**Version Conflict**:
```bash
npm view @a24z/pixeltable-sdk versions  # Check existing versions
```

### Build Issues

**TypeScript Errors**:
```bash
cd js-sdk
bun run typecheck  # Check for type errors
```

**Missing Dependencies**:
```bash
cd js-sdk
rm -rf node_modules
bun install
```

### PyPI Publishing Issues

**Authentication**:
```bash
# Create ~/.pypirc with credentials
# Or use token authentication
python -m twine upload --repository pypi dist/*
```

**Build Issues**:
```bash
# Clean build artifacts
rm -rf dist/ build/ *.egg-info
# Rebuild
uv build
```

## Security Considerations

### npm Security

1. **2FA Required**: Enable two-factor authentication on npm
2. **Scoped Package**: Using `@a24z/` scope for organization control
3. **Lock Files**: Commit `bun.lockb` for reproducible builds

### PyPI Security

1. **API Tokens**: Use API tokens instead of passwords
2. **Signed Releases**: Consider GPG signing releases
3. **SBOM**: Generate Software Bill of Materials for compliance

## Monitoring

### Package Usage

Track adoption and issues:
- npm: https://www.npmjs.com/package/@a24z/pixeltable-sdk
- PyPI: https://pypi.org/project/pixeltable/
- GitHub Issues: Monitor for user-reported problems

### Version Adoption

```bash
# Check npm download stats
npm view @a24z/pixeltable-sdk downloads

# Check PyPI download stats  
pip install pypistats
pypistats recent pixeltable
```

## Rollback Procedure

If a bad version is published:

### npm Deprecation

```bash
npm deprecate @a24z/pixeltable-sdk@0.1.1 "Critical bug, use 0.1.2"
```

### npm Unpublish (within 72 hours)

```bash
npm unpublish @a24z/pixeltable-sdk@0.1.1
```

### PyPI (cannot unpublish)

- Yank the release on PyPI web interface
- Publish a new patch version immediately
- Document the issue in CHANGELOG

## Future Improvements

1. **Automated Releases**: GitHub Actions for tag-based publishing
2. **Canary Releases**: Automated builds from main branch
3. **Package Provenance**: npm and PyPI signed attestations
4. **Multi-Platform Testing**: Ensure compatibility across Node versions
5. **API Versioning**: Implement versioned endpoints (v1, v2)
6. **SDK Code Generation**: Auto-generate from OpenAPI spec

## Contact

For publishing access or issues:
- npm org: Contact `@a24z` organization admins
- PyPI: Contact project maintainers
- Internal: File issue in GitHub repository