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
    # 1. Block Caching (Fixes "Storable and Cacheable Content")
    # Ensures browsers do not store sensitive data locally
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    # 2. Strong Content Security Policy (CSP) (Fixes "CSP: Failure to Define Directive")
    # Explicitly defines allowed sources for scripts, styles, images, etc.
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "  # Allow inline scripts for demo simplicity
        "style-src 'self' 'unsafe-inline'; "   # Allow inline styles for demo simplicity
        "img-src 'self' data:; "               # Allow images from self and data URIs
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "             # Prevents this site from being framed (Clickjacking)
        "object-src 'none'; "                  # Blocks plugins like Flash/Java
        "base-uri 'self';"
    )
    response.headers['Content-Security-Policy'] = csp

    # 3. Security Isolation (Fixes "Insufficient Site Isolation" / Spectre)
    # These headers isolate the browsing context to prevent cross-origin attacks
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'

    # 4. Standard Hardening Headers
    response.headers['X-Frame-Options'] = 'DENY'        # Prevent Clickjacking
    response.headers['X-Content-Type-Options'] = 'nosniff' # Prevent MIME Sniffing
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains' # Force HTTPS
    
    # 5. Hide Server Version (Fixes "Server Leaks Version Information")
    response.headers['Server'] = 'Secure-Shop-Server'
    
    # 6. Permissions Policy (Hardware access restriction)
    response.headers['Permissions-Policy'] = "geolocation=(), microphone=(), camera=()"

    return response

@app.route("/")
def home():
    try:
        # Fetch products from the backend microservice
        response = requests.get(f"{API_URL}/products", timeout=2)
        products = response.json()
    except Exception as e:
        # Fallback if backend is down
        print(f"Error fetching products: {e}")
        products = []
    return render_template("index.html", products=products)

@app.route("/health")
def health():
    return "healthy", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
