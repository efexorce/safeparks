#!/usr/bin/env bash
set -euo pipefail

echo "SafeParks kurulum scripti baslatiliyor..."

if ! command -v docker &>/dev/null; then
  echo "HATA: Docker kurulu degil."
  exit 1
fi

if ! command -v docker compose &>/dev/null && ! docker compose version &>/dev/null 2>&1; then
  echo "HATA: Docker Compose kurulu degil."
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [ ! -f "$PROJECT_ROOT/backend/.env" ]; then
  cp "$PROJECT_ROOT/backend/.env.example" "$PROJECT_ROOT/backend/.env"
  echo ".env dosyasi olusturuldu: $PROJECT_ROOT/backend/.env"
  echo "Lutfen backend/.env dosyasini duzenleyin."
fi

echo "Docker imajlari olusturuluyor..."
docker compose -f "$PROJECT_ROOT/infrastructure/docker/docker-compose.yml" build

echo "Servisler baslatiliyor..."
docker compose -f "$PROJECT_ROOT/infrastructure/docker/docker-compose.yml" up -d postgres redis mosquitto

echo "Veritabani hazir olana kadar bekleniyor (30s)..."
sleep 30

echo "Migrasyonlar calistiriliyor..."
docker compose -f "$PROJECT_ROOT/infrastructure/docker/docker-compose.yml" run --rm backend \
  alembic upgrade head

echo "Tum servisler baslatiliyor..."
docker compose -f "$PROJECT_ROOT/infrastructure/docker/docker-compose.yml" up -d

echo ""
echo "SafeParks basariyla kuruldu!"
echo "Backend API: http://localhost:8000/api/v1/docs"
echo "Frontend:    http://localhost:3000"
echo "MQTT Broker: localhost:1883"
