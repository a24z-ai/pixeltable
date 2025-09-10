#!/bin/bash
# Publish the JavaScript SDK to npm

set -e

echo "📦 Publishing @a24z/pixeltable-sdk to npm..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Move to js-sdk directory
cd js-sdk

# Check if logged in to npm
if ! npm whoami &>/dev/null; then
    echo -e "${RED}❌ Not logged in to npm${NC}"
    echo "Please run: npm login"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(node -p "require('./package.json').version")
echo -e "Current version: ${YELLOW}$CURRENT_VERSION${NC}"

# Prompt for version bump
echo "How would you like to bump the version?"
echo "1) Patch (x.x.X)"
echo "2) Minor (x.X.0)"
echo "3) Major (X.0.0)"
echo "4) Custom"
echo "5) No bump (publish current version)"
read -p "Choose [1-5]: " choice

case $choice in
    1)
        NEW_VERSION=$(npm version patch --no-git-tag-version)
        ;;
    2)
        NEW_VERSION=$(npm version minor --no-git-tag-version)
        ;;
    3)
        NEW_VERSION=$(npm version major --no-git-tag-version)
        ;;
    4)
        read -p "Enter new version: " NEW_VERSION
        npm version $NEW_VERSION --no-git-tag-version
        NEW_VERSION="v$NEW_VERSION"
        ;;
    5)
        NEW_VERSION="v$CURRENT_VERSION"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "Publishing version: ${GREEN}$NEW_VERSION${NC}"

# Run pre-publish checks
echo "🔍 Running pre-publish checks..."
bun run lint
bun test

# Build the package
echo "🔨 Building package..."
bun run build

# Dry run first
echo "🧪 Performing dry run..."
npm publish --dry-run

# Confirm publication
echo -e "${YELLOW}Ready to publish @a24z/pixeltable-sdk@$NEW_VERSION to npm${NC}"
read -p "Continue? (y/N): " confirm

if [[ $confirm != [yY] ]]; then
    echo "Publication cancelled"
    exit 1
fi

# Publish to npm
echo "🚀 Publishing to npm..."
npm publish

echo -e "${GREEN}✅ Successfully published @a24z/pixeltable-sdk@$NEW_VERSION${NC}"
echo ""
echo "Next steps:"
echo "1. Commit the version bump: git add package.json && git commit -m \"chore: bump @a24z/pixeltable-sdk to $NEW_VERSION\""
echo "2. Create a git tag: git tag js-sdk-$NEW_VERSION"
echo "3. Push changes: git push && git push --tags"