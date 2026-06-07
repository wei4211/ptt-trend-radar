#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🛑 Stopping PTT Trend Radar..."
lsof -ti :8001 | xargs kill -9 2>/dev/null || true
lsof -ti :3000 | xargs kill -f 2>/dev/null || true
pkill -f "ptt/frontend" 2>/dev/null || true
docker compose -f "$PROJECT_DIR/docker-compose.dev.yml" stop 2>/dev/null || true
echo "✅ All stopped."
