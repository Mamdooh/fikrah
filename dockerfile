FROM python:3.11-slim

WORKDIR /app

# Install Flask and Prometheus client
RUN pip install flask prometheus-client

COPY app.py .

# Expose port 5000
EXPOSE 5000

CMD ["python", "app.py"]