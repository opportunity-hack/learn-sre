# Monitoring Demo

A FastAPI application with full observability stack including Prometheus, Tempo, and Grafana.

## Local Development

1. Build and run:
```bash
docker-compose up --build
```

2. Access:
- App: http://localhost:8000
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

## Fly.io Deployment

1. Install Fly CLI:
```bash
curl -L https://fly.io/install.sh | sh
flyctl auth login
```

2. Deploy:
```bash
fly launch
fly volumes create tempo_data --size 1
fly volumes create prometheus_data --size 1
fly volumes create grafana_data --size 1
fly deploy
```

## Endpoints

- `/`: Health check
- `/products/{product_id}`: Get product details
- `/metrics`: Prometheus metrics

## Monitoring

- Metrics: Available in Prometheus
- Traces: Available in Tempo
- Dashboards: Preconfigured in Grafana


# Architecture Overview

This application implements a modern observability stack with the following components:

## User Interface Layer
- **Browser**: Accesses the application through port 5173
- **Frontend**: React application serving the user interface
- **Frontend Metrics**: Dedicated service collecting frontend telemetry (port 9091)

## Application Layer
- **Backend API**: FastAPI service handling business logic (port 8000)
- Communicates with observability services for monitoring and tracing

## Observability Stack
- **Prometheus**: Metrics collection and storage (port 9090)
- **Tempo**: Distributed tracing backend (ports 4317, 3200)
- **Grafana**: Visualization and dashboards (port 3000)
- **Memcached**: Caching layer for Tempo

## Persistent Storage
- Dedicated volumes for Prometheus, Grafana, and Tempo data
- Ensures data persistence across container restarts

## Key Features
- Complete observability pipeline with metrics, traces, and visualization
- Frontend and backend telemetry collection
- Persistent storage for all observability data
- Containerized services with health checks
- Automatic service discovery and configuration


```
📱 User (Browser)
          |
          | :5173
          ▼
  +----------------+            +-----------------+
  |    Frontend    |---------->|  Frontend       |
  |    (React)     |   :9091  |   Metrics       |
  +----------------+            +-----------------+
          |                            |
          | :8000                      |
          ▼                            |
  +----------------+                   |
  |    Backend     |                   |
  |    (FastAPI)   |                   |
  +----------------+                   |
          |                           |
          |                           |
    :4317 |                          | :9090
          ▼                          ▼
  +----------------+            +-----------------+
  |     Tempo      |<----------|   Prometheus    |
  |   (Tracing)    |            |    (Metrics)   |
  +----------------+            +-----------------+
          |                            |
          |                            |
          |            +---------------+
          |            |
          ▼            ▼
  +--------------------------------+
  |           Grafana              |
  |  (Dashboards & Visualization)  |
  |            :3000               |
  +--------------------------------+
              |
    +---------+---------+
    |                   |
+----------+      +-----------+
|  Tempo   |      |Prometheus |
| Volume   |      |  Volume   |
+----------+      +-----------+
```