FROM python:3.11-slim

WORKDIR /app

# Install Flask
RUN pip install flask

COPY app.py .

# Expose port 5000
EXPOSE 5000

CMD ["python", "app.py"]