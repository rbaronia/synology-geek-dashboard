#!/usr/bin/env bash
# package-for-nas.sh — Creates a clean zip archive ready to upload to DSM File Station
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

ZIP_NAME="synology-dashboard-update.zip"

rm -f "$ZIP_NAME"

echo "📦 Creating $ZIP_NAME (excluding .env, .venv, .git, caches)..."
zip -r "$ZIP_NAME" . \
  -x ".env*" \
  -x ".venv*" \
  -x ".git*" \
  -x "*__pycache__*" \
  -x "*.DS_Store" \
  -x "*.zip"

echo "=========================================================="
echo "✅ Package created: $ZIP_NAME"
echo ""
echo "Steps in Synology DSM Web UI:"
echo "1. Open File Station -> /docker/synology-dashboard/"
echo "2. Drag and drop $ZIP_NAME into the folder"
echo "3. Right-click $ZIP_NAME -> 'Extract here' (Overwrites code, leaves .env safe)"
echo "4. Open Container Manager -> Project -> synology-dashboard -> Action -> Build/Restart"
echo "=========================================================="
