from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello world from Python app!\nAWS test\nCI/CD is working!\n Testing auto deploy66"

@app.route('/health')
def health():
    return "Status: Healthy\n"

@app.route('/version')
def version():
    return "Version: 1.0.0\nBuild: DevOps Pipeline\n"

@app.route('/about')
def about():
    return "DevOps Learning Project\nPython Flask + Docker + GitHub Actions + AWS\n"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)