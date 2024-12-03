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