# --> [Google Slides](https://docs.google.com/presentation/d/1EnIlTz4GOn7v_loYxYFGeaaMxbpW5xnK3mo23KMuIFc/edit?usp=sharing)

# Monitoring Demo

A FastAPI application with full observability stack including Prometheus, Tempo, and Grafana.

## Local Development

1. Build and run:
```bash
docker-compose up --build
```
**NOTE:** It takes a hot 20 seconds for everything to start

To wipe clean and start new
```
docker-compose down -v
```

2. Access:
- Frontend: http://localhost:5173 
 - Frontend metrics: http://localhost:9001
- Backend: http://localhost:8000
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

## Load Test
```
pip install aiohttp rich
python load_test.py --url http://localhost:8001 --requests 1000 --concurrent 10
```
https://orange-waddle-v7wpg56q6pcwgqr-8000.app.github.dev/
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
- **[Tempo](https://grafana.com/docs/tempo/next/getting-started/docker-example/)**: Distributed tracing backend (ports 4317, 3200)
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