# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the remaining files
COPY . /app

# Expose port
EXPOSE 8080

# Run the app
CMD ["python", "app.py"]
