# Use minimal Python image
FROM python:3.11-slim

# Install curl for debugging
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install dependencies (ensure Kubernetes + Prometheus client are installed)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the green scheduler code
COPY green_scheduler.py /app/green_scheduler.py

# Disable bytecode caching and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose metrics port
EXPOSE 9100

# Run the Kubernetes scheduler (not Flask)
CMD ["python3", "/app/green_scheduler.py"]
