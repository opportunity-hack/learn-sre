from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest, multiprocess, CollectorRegistry
import random
import time
from datetime import datetime
import logging
from contextlib import asynccontextmanager
from .monitoring import setup_monitoring, REQUEST_COUNT, REQUEST_LATENCY, ERROR_COUNT
import json

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    yield
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)

# Get tracer
tracer = setup_monitoring(app)

# Initialize the Prometheus registry
registry = CollectorRegistry()

@app.get("/metrics")
async def metrics():
    return Response(
        generate_latest(),  # Remove registry parameter as it's not needed
        media_type=CONTENT_TYPE_LATEST
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data
PRODUCTS = {
    1: {"name": "Laptop", "price": 999.99, "stock": 10, "id": 1 },
    2: {"name": "Smartphone", "price": 499.99, "stock": 20, "id": 2},
    3: {"name": "Headphones", "price": 99.99, "stock": 100, "id": 3},
}

@app.get("/")
async def read_root():
    with tracer.start_as_current_span("root_request") as span:
        REQUEST_COUNT.labels(endpoint="/", status="success").inc()
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    with tracer.start_as_current_span("get_product") as span:
        start_time = time.time()
        try:
            # Add more detailed span attributes
            span.set_attribute("product.id", product_id)
            span.set_attribute("request.type", "get_product")
            
            if product_id not in PRODUCTS:
                span.set_attribute("error", True)
                span.set_attribute("error.type", "not_found")
                ERROR_COUNT.labels(error_type="not_found").inc()
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Add product details to span
            product = PRODUCTS[product_id]
            span.set_attribute("product.name", product["name"])
            span.set_attribute("product.price", product["price"])
            span.set_attribute("product.stock", product["stock"])
            span.set_attribute("status", "success")
            span.set_attribute("response.type", "product")
            span.set_attribute("response.status", 200)
            span.set_attribute("endpoint", "/products")

            
            REQUEST_COUNT.labels(endpoint="/products", status="success").inc()
            return product
            
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            REQUEST_COUNT.labels(endpoint="/products", status="error").inc()
            logger.error(f"Error fetching product {product_id}: {str(e)}")
            raise
        finally:
            REQUEST_LATENCY.labels(endpoint="/products").observe(
                time.time() - start_time
            )

@app.post("/products/{product_id}/purchase")
async def purchase_product(product_id: int):
    with tracer.start_as_current_span("purchase_product") as span:
        start_time = time.time()
        try:
            span.set_attribute("product.id", product_id)
            span.set_attribute("request.type", "purchase_product")
            
            if product_id not in PRODUCTS:
                span.set_attribute("error", True)
                span.set_attribute("error.type", "not_found")
                ERROR_COUNT.labels(error_type="not_found").inc()
                raise HTTPException(status_code=404, detail="Product not found")
            
            product = PRODUCTS[product_id]
            if product["stock"] <= 0:
                span.set_attribute("error", True)
                span.set_attribute("error.type", "out_of_stock")
                ERROR_COUNT.labels(error_type="out_of_stock").inc()
                raise HTTPException(status_code=400, detail="Product out of stock")
            
            # Simulate purchase by reducing stock
            PRODUCTS[product_id]["stock"] -= 1
            
            span.set_attribute("product.name", product["name"])
            span.set_attribute("product.remaining_stock", product["stock"])
            span.set_attribute("status", "success")
            span.set_attribute("endpoint", "/purchase")
            
            REQUEST_COUNT.labels(endpoint="/purchase", status="success").inc()
            return {"message": "Purchase successful", "remaining_stock": product["stock"]}
            
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            REQUEST_COUNT.labels(endpoint="/purchase", status="error").inc()
            logger.error(f"Error processing purchase for product {product_id}: {str(e)}")
            raise
        finally:
            REQUEST_LATENCY.labels(endpoint="/purchase").observe(
                time.time() - start_time
            )
     