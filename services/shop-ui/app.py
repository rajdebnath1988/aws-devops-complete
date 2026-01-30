from flask import Flask, render_template, jsonify, make_response
import requests
import os

app = Flask(__name__)

API_URL = os.getenv("PRODUCT_API_URL", "http://localhost:8000")

# -------------------------------------------------------------
# SECURITY MIDDLEWARE (Fixes ZAP Warnings)
# -------------------------------------------------------------
@app.after_request
def add_security_headers(response):
    # Prevent Clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevent MIME-Sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Basic Content Security Policy (Adjust 'self' as needed)
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    
    # Hide Server Info (Optional, but good practice)
    response.headers['Server'] = 'DevOps-Server'
    
    # Enforce Permissions Policy
    response.headers['Permissions-Policy'] = "geolocation=(), microphone=(), camera=()"
    
    return response

@app.route("/")
def home():
    try:
        response = requests.get(f"{API_URL}/products", timeout=2)
        products = response.json()
    except Exception as e:
        products = []
    return render_template("index.html", products=products)

@app.route("/health")
def health():
    return "healthy", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
