// src/monitoring.ts
import axios from 'axios';

class MonitoringService {
    private metricsEndpoint = 'http://localhost:9091/collect';

    async recordApiLatency(endpoint: string, duration: number) {
        await this.sendMetric('frontend_api_latency', duration, { endpoint });
    }

    async recordApiResult(endpoint: string, success: boolean) {
        await this.sendMetric('frontend_api_result', success ? 1 : 0, { endpoint, status: success ? 'success' : 'error' });
    }

    async recordProductAvailability(productId: number, inStock: boolean) {
        await this.sendMetric('frontend_product_availability', inStock ? 1 : 0, { product_id: String(productId) });
    }

    async recordPurchaseAttempt(productId: number, success: boolean) {
        await this.sendMetric('frontend_purchase_attempt', 1, { 
            product_id: String(productId),
            status: success ? 'success' : 'error'
        });
    }

    private async sendMetric(name: string, value: number, labels: Record<string, string>) {
        try {
            await axios.post(this.metricsEndpoint, {
                name,
                value,
                labels,
                timestamp: Date.now()
            });
        } catch (error) {
            console.error('Failed to send metric:', error);
        }
    }
}

export const monitoring = new MonitoringService();
