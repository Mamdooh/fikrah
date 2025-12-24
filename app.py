from flask import Flask, Response, request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import random

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'app_request_count', 
    'Total Request Count', 
    ['method', 'endpoint', 'status', 'country']
)
REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds', 
    'Request latency', 
    ['endpoint']
)
ERROR_COUNT = Counter(
    'app_error_count',
    'Total Error Count',
    ['endpoint', 'error_type']
)
ACTIVE_USERS = Gauge(
    'app_active_users',
    'Currently active users by country',
    ['country']
)
ROUTE_VISITS = Counter(
    'app_route_visits',
    'Visits per route/page',
    ['route', 'country']
)

# Simple IP to country mapping (mock data for demo)
# In production, you'd use a real GeoIP service
def get_country_from_ip(ip):
    """Mock function - maps IP to country for demo"""
    # You can use a real service like ipapi.co or MaxMind GeoIP
    country_map = {
        '127.0.0.1': 'Local',
        '::1': 'Local'
    }
    
    # For demo: random countries for different IPs
    if ip not in country_map:
        countries = ['USA', 'UK', 'Germany', 'France', 'Japan', 'Canada', 'Australia']
        return random.choice(countries)
    
    return country_map.get(ip, 'Unknown')

@app.before_request
def before_request():
    request.start_time = time.time()
    
    # Get user's country
    user_ip = request.remote_addr
    request.user_country = get_country_from_ip(user_ip)
    
    # Track active users (simplified)
    ACTIVE_USERS.labels(country=request.user_country).inc()

@app.after_request
def after_request(response):
    request_latency = time.time() - request.start_time
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method, 
        endpoint=request.endpoint or 'unknown',
        status=response.status_code,
        country=request.user_country
    ).inc()
    
    REQUEST_LATENCY.labels(
        endpoint=request.endpoint or 'unknown'
    ).observe(request_latency)
    
    ROUTE_VISITS.labels(
        route=request.path,
        country=request.user_country
    ).inc()
    
    # Decrement active users
    ACTIVE_USERS.labels(country=request.user_country).dec()
    
    return response

@app.errorhandler(404)
def not_found(error):
    # Manually record the error
    ERROR_COUNT.labels(endpoint=request.endpoint or 'not_found', error_type='404').inc()
    
    # Also record in request count
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint or 'not_found',
        status=404,
        country=getattr(request, 'user_country', 'Unknown')
    ).inc()
    
    # Record route visit
    ROUTE_VISITS.labels(
        route=request.path,
        country=getattr(request, 'user_country', 'Unknown')
    ).inc()
    
    return "404 - Page Not Found\n", 404

@app.errorhandler(403)
def forbidden_handler(error):
    # Manually record the error
    ERROR_COUNT.labels(endpoint=request.endpoint or 'forbidden', error_type='403').inc()
    
    # Also record in request count
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint or 'forbidden',
        status=403,
        country=getattr(request, 'user_country', 'Unknown')
    ).inc()
    
    # Record route visit
    ROUTE_VISITS.labels(
        route=request.path,
        country=getattr(request, 'user_country', 'Unknown')
    ).inc()
    
    return "403 - Forbidden\n", 403

@app.errorhandler(500)
def internal_error(error):
    # Manually record the error
    ERROR_COUNT.labels(endpoint=request.endpoint or 'error', error_type='500').inc()
    
    # Also record in request count
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint or 'error',
        status=500,
        country=getattr(request, 'user_country', 'Unknown')
    ).inc()
    
    return "500 - Internal Server Error\n", 500

# Add this to app.py for testing
@app.route('/admin')
def admin():
    # BAD: SQL Injection vulnerability (Qodana will catch this!)
    user_input = request.args.get('user', '')
    query = f"SELECT * FROM users WHERE username = '{user_input}'"  # Vulnerable!
    return f"Query: {query}\n"

@app.route('/debug')
def debug():
    # BAD: Exposing sensitive info (Qodana will catch this!)
    import os
    return str(os.environ)  # Never expose environment variables!

@app.errorhandler(Exception)
def handle_exception(error):
    # Catch all other exceptions
    ERROR_COUNT.labels(endpoint=request.endpoint or 'exception', error_type='exception').inc()
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint or 'exception',
        status=500,
        country=getattr(request, 'user_country', 'Unknown')
    ).inc()
    
    return f"500 - Error: {str(error)}\n", 500

@app.route('/')
def hello():
    return f"Hello from {request.user_country}!\nWelcome to our DevOps monitoring demo!\n"

@app.route('/health')
def health():
    return "Status: Healthy\n"

@app.route('/version')
def version():
    return "Version: 2.0.0 with Enhanced Monitoring\n"

@app.route('/about')
def about():
    return "DevOps Learning Project\nPython Flask + Docker + GitHub Actions + AWS + Grafana\n"

@app.route('/status')
def status():
    return "Server is running with full monitoring!\n"

@app.route('/deploy')
def deploy():
    return "Auto-deployed from GitHub Actions to AWS ECS!\n"

@app.route('/dashboard')
def dashboard():
    return f"Dashboard Page - Visitor from {request.user_country}\n"

@app.route('/api/data')
def api_data():
    return f"API Data Endpoint - Request from {request.user_country}\n"

@app.route('/products')
def products():
    return f"Products Page - Showing products for {request.user_country}\n"

@app.route('/forbidden')
def forbidden_route():
    """This route always returns 403"""
    return "You don't have permission to access this!", 403

@app.route('/buggy')
def buggy_endpoint():
    """This route throws an exception"""
    # Simulate different types of errors
    error_type = random.choice(['division', 'type', 'value'])
    
    if error_type == 'division':
        result = 1 / 0  # Division by zero - will be caught by errorhandler
    elif error_type == 'type':
        result = "text" + 123  # Type error - will be caught by errorhandler
    else:
        raise ValueError("Simulated error for monitoring!")
    
    return str(result)

@app.route('/slow')
def slow_endpoint():
    """Simulates a slow endpoint"""
    time.sleep(random.uniform(1, 3))  # Random delay 1-3 seconds
    return "This was a slow request!\n"

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)