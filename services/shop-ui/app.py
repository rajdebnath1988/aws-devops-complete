from flask import Flask, render_template, jsonify, make_response
import requests
import os

app = Flask(__name__)

API_URL = os.getenv("PRODUCT_API_URL", "http://localhost:8000")

# -------------------------------------------------------------
# ULTRA-SECURE MIDDLEWARE (Fixes ZAP Warnings)
# -------------------------------------------------------------
@app.after_request
def add_security_headers(response):
    # 1. Block Caching (Fixes "Non-Storable Content" warning)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    # 2. Strong CSP (Fixes "CSP: Failure to Define Directive")
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "object-src 'none'; "
        "base-uri 'self';"
    )
    response.headers['Content-Security-Policy'] = csp

    # 3. Security Isolation (Fixes "Insufficient Site Isolation" / Spectre)
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'

    # 4. Standard Hardening
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # 5. Hide Server Version (Fixes "Server Leaks Version Information")
    response.headers['Server'] = 'Secure-Shop'

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
