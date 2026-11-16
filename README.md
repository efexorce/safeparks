# SafeParks

Smart safety and monitoring platform for city parks. Edge devices analyse camera streams on site, raise alarms when something needs attention, and switch cameras to a low-bitrate mode when nothing is moving, so that a park can be covered over a limited mobile data plan and power budget.

This repository is a prototype: the services are wired together end to end, but there is no automated test suite yet.

## How it works

```
 Camera (RTSP) ──> Edge AI node ──HTTP/MQTT──> Backend API ──WebSocket──> Dashboard
                   motion + event               FastAPI                  React
                   detection (ONNX)             TimescaleDB, Redis, Kafka
```

- **Edge AI (`edge_ai/`)** reads an RTSP stream, runs motion detection and an ONNX object-detection model, and reports motion changes and detected events to the backend. A bandwidth optimiser moves a camera between a high-quality profile (1080p, 25 fps) and a low-quality one (480p, 5 fps) depending on activity.
- **Backend (`backend/`)** is a FastAPI service with endpoints for authentication, cameras, alarms, energy usage and reports, plus a WebSocket channel for live updates. It stores data in PostgreSQL/TimescaleDB and uses MQTT, Kafka and Redis for messaging and caching.
- **Dashboard (`frontend/`)** is a React + TypeScript single-page app with an overview, camera list, alarm queue, map view, energy charts and daily/monthly reports.
- **Infrastructure (`infrastructure/`)** contains the Docker Compose stack, Kubernetes manifests, the nginx reverse proxy configuration and a setup script.

Alarm types handled by the dashboard include person down, suspicious object, intrusion, fire and flood.

## Getting started

Requirements: Docker with the Compose plugin.

```bash
cp backend/.env.example backend/.env      # then set POSTGRES_PASSWORD and SECRET_KEY
./infrastructure/scripts/setup.sh
```

The setup script builds the images and starts the stack defined in `infrastructure/docker/docker-compose.yml`:

| Service | Port |
| --- | --- |
| Backend API | 8000 (docs at `/api/v1/docs`) |
| Dashboard | 3000 |
| nginx | 80, 443 |
| PostgreSQL / TimescaleDB | 5432 |
| Redis | 6379 |
| MQTT (Mosquitto) | 1883, 9001 |
| Kafka | 29092 |

The passwords in `docker-compose.yml` and `.env.example` are development placeholders. Change them before exposing the stack to a network.

### Running an edge node

```bash
pip install -r edge_ai/requirements.txt
BACKEND_URL=http://localhost:8000 \
CAMERA_ID=<camera id> \
RTSP_URL=rtsp://<camera address>/stream \
MODEL_PATH=edge_ai/models/<model>.onnx \
python -m edge_ai.main
```

No model file is included. `edge_ai/models/model_manager.py` describes how to obtain a YOLOv8-nano ONNX model and how to convert it for Hailo-8 or NVIDIA Jetson (TensorRT).

## Project layout

```
backend/          FastAPI application, SQLAlchemy models, Alembic migrations
edge_ai/          Stream processing, motion and event detection, model loading
frontend/         React dashboard (Vite, Tailwind CSS, Leaflet, Recharts)
infrastructure/   Docker Compose, Kubernetes, nginx, setup script
```

## Language

The dashboard interface and some log and notification messages are currently in Turkish.
