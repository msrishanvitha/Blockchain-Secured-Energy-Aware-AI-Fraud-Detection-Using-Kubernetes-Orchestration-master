# Step 1: build stage
FROM python:3.11-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 2: final distroless image
FROM gcr.io/distroless/python3
WORKDIR /app
COPY --from=build /app /app
COPY . /app
USER nonroot
CMD ["main.py"]
