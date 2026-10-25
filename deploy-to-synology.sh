#!/usr/bin/env bash
# deploy-to-synology.sh — Automated 1-command remote deployment to Synology NAS
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Source .env if present
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

NAS_TARGET="${NAS_HOST:-10.0.0.91}"
SSH_USER="${SSH_USER:-admin}"
SSH_PORT="${SSH_PORT:-22}"
REMOTE_DIR="/volume1/docker/synology-dashboard"

echo "=========================================================="
echo "⚡ Automated Synology NAS Deployment: ${NAS_TARGET}"
echo "=========================================================="

echo "📁 [1/3] Ensuring remote directory ${REMOTE_DIR} exists..."
ssh -p "$SSH_PORT" -o StrictHostKeyChecking=no "${SSH_USER}@${NAS_TARGET}" "sudo mkdir -p ${REMOTE_DIR} && sudo chown -R ${SSH_USER} ${REMOTE_DIR}"

echo "📤 [2/3] Transferring project files..."
rsync -avz -e "ssh -p $SSH_PORT" \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.git' \
  ./ "${SSH_USER}@${NAS_TARGET}:${REMOTE_DIR}/"

echo "🚀 [3/3] Building and starting container in background..."
ssh -p "$SSH_PORT" "${SSH_USER}@${NAS_TARGET}" "cd ${REMOTE_DIR} && sudo docker compose up -d --build"

echo "=========================================================="
echo "✅ Dashboard is LIVE at: http://${NAS_TARGET}:8000"
echo "=========================================================="
