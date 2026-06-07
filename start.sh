#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$PROJECT_DIR/.env"

# Load .env
if [ -f "$ENV_FILE" ]; then
  export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

echo "🚀 Starting PTT Trend Radar..."

# 1. Start DB
echo "📦 Starting PostgreSQL..."
docker compose -f "$PROJECT_DIR/docker-compose.dev.yml" up -d
echo "⏳ Waiting for DB to be ready..."
until docker exec ptt-db-1 pg_isready -U ptt -q 2>/dev/null; do
  sleep 1
done
echo "✅ DB ready"

# 2. Kill any existing backend
lsof -ti :8001 | xargs kill -9 2>/dev/null || true
sleep 1

# 3. Start backend
echo "🐍 Starting FastAPI backend on :8001..."
cd "$PROJECT_DIR/backend"
DATABASE_URL="postgresql+asyncpg://ptt:pttpassword@localhost:5432/ptt_radar" \
GEMINI_API_KEY="${GEMINI_API_KEY:-}" \
  uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8001 \
    --log-level warning \
    > /tmp/ptt_backend.log 2>&1 &

BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend health
echo "⏳ Waiting for backend..."
for i in $(seq 1 20); do
  if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Backend ready"
    break
  fi
  sleep 1
done

# 4. Start frontend
echo "🌐 Starting React frontend on :3000..."
cd "$PROJECT_DIR/frontend"
npm run dev > /tmp/ptt_frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

sleep 3
echo ""
echo "✅ PTT Trend Radar is running!"
echo "   Frontend : http://localhost:3000"
echo "   API      : http://localhost:8001"
echo "   API Docs : http://localhost:8001/docs"
echo ""
echo "📰 To scrape articles now:"
echo "   curl -X POST http://localhost:8001/api/scraper/trigger/sync"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep running, kill children on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker compose -f $PROJECT_DIR/docker-compose.dev.yml stop; echo '👋 Stopped.'" EXIT
wait
