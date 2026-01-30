from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import boto3
import os
import time

app = FastAPI()

# -------------------------------
# PROMETHEUS METRICS
# -------------------------------
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "Request Latency",
    ["endpoint"]
)

# -------------------------------
# AWS SSM Integration
# -------------------------------
def get_ssm_param(param_name):
    try:
        ssm = boto3.client('ssm', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        response = ssm.get_parameter(Name=param_name, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        print(f"Failed to fetch SSM param: {e}")
        return "local-mode"

# -------------------------------
# MIDDLEWARE FOR METRICS
# -------------------------------
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_LATENCY.labels(endpoint=request.url.path).observe(latency)

    return response

# -------------------------------
# API ROUTES
# -------------------------------
@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/products")
def get_products():
    env_mode = get_ssm_param('/devops-demo/environment')

    return [
        {"id": 101, "name": "Kubernetes Guide", "price": 29.99, "env": env_mode},
        {"id": 102, "name": "AWS DevOps Handbook", "price": 39.99, "env": env_mode},
        {"id": 103, "name": "Python Microservices", "price": 49.99, "env": env_mode}
    ]

# -------------------------------
# PROMETHEUS SCRAPE ENDPOINT
# -------------------------------
@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}
