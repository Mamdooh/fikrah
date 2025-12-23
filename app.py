from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello world from Python app!\nAWS test\nCI/CD is working!\n"

@app.route('/health')
def health():
    return "Status: Healthy\n"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)