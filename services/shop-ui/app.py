from flask import Flask, render_template, jsonify
import requests
import os

app = Flask(__name__)

# Service Discovery via Env Var (Injected by K8s)
API_URL = os.getenv("PRODUCT_API_URL", "http://localhost:8000")

@app.route("/")
def home():
    try:
        # Call the Microservice
        response = requests.get(f"{API_URL}/products", timeout=2)
        products = response.json()
    except Exception as e:
        products = []
        error = str(e)
    return render_template("index.html", products=products)

@app.route("/health")
def health():
    return "healthy", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
