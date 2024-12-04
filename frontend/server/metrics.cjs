const express = require('express');
const promClient = require('prom-client');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });

// Define metrics
const pageLoadTime = new promClient.Histogram({
  name: 'frontend_page_load_time_seconds',
  help: 'Time taken to load pages',
  labelNames: ['page'],
  registers: [register]
});

const userInteractions = new promClient.Counter({
  name: 'frontend_user_interactions_total',
  help: 'Count of user interactions',
  labelNames: ['action'],
  registers: [register]
});

const frontendErrors = new promClient.Counter({
  name: 'frontend_errors_total',
  help: 'Count of frontend errors',
  labelNames: ['type'],
  registers: [register]
});

const apiLatencyHistogram = new promClient.Histogram({
    name: 'frontend_api_latency',
    help: 'API request latency in milliseconds',
    labelNames: ['endpoint']
});

const apiResultCounter = new promClient.Counter({
    name: 'frontend_api_result',
    help: 'API request results (success/error)',
    labelNames: ['endpoint', 'status']
});

const productAvailabilityGauge = new promClient.Gauge({
    name: 'frontend_product_availability',
    help: 'Product availability status',
    labelNames: ['product_id']
});

const purchaseAttemptsCounter = new promClient.Counter({
    name: 'frontend_purchase_attempt',
    help: 'Purchase attempts count',
    labelNames: ['product_id', 'status']
});

app.post('/collect', (req, res) => {
    const { name, value, labels } = req.body;
    
    switch(name) {
        case 'frontend_api_latency':
            apiLatencyHistogram.labels(labels.endpoint).observe(value);
            break;
        case 'frontend_api_result':
            apiResultCounter.labels(labels.endpoint, labels.status).inc();
            break;
        case 'frontend_product_availability':
            productAvailabilityGauge.labels(labels.product_id).set(value);
            break;
        case 'frontend_purchase_attempt':
            purchaseAttemptsCounter.labels(labels.product_id, labels.status).inc();
            break;
    }
    
    res.sendStatus(200);
});

app.get('/metrics', async (req, res) => {
    res.set('Content-Type', promClient.register.contentType);
    res.end(await promClient.register.metrics());
});

app.post('/metric/pageload', (req, res) => {
  pageLoadTime.observe({ page: req.body.page }, req.body.duration);
  res.send('ok');
});

app.post('/metric/interaction', (req, res) => {
  userInteractions.inc({ action: req.body.action });
  res.send('ok');
});

app.post('/metric/error', (req, res) => {
  frontendErrors.inc({ type: req.body.type });
  res.send('ok');
});

app.listen(9091, () => {
    console.log('Metrics server listening on port 9091');
});