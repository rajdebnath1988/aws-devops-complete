from fastapi import FastAPI
import boto3
import os

app = FastAPI()

# AWS SSM Integration to fetch "Secret" config
def get_ssm_param(param_name):
    try:
        ssm = boto3.client('ssm', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        response = ssm.get_parameter(Name=param_name, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        print(f"Failed to fetch SSM param: {e}")
        return "local-mode"

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/products")
def get_products():
    # Simulate fetching data based on an environment flag from SSM
    env_mode = get_ssm_param('/devops-demo/environment')
    
    return [
        {"id": 101, "name": "Kubernetes Guide", "price": 29.99, "env": env_mode},
        {"id": 102, "name": "AWS DevOps Handbook", "price": 39.99, "env": env_mode},
        {"id": 103, "name": "Python Microservices", "price": 49.99, "env": env_mode}
    ]
