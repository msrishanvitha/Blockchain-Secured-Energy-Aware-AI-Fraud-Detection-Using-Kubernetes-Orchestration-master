FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install kubernetes prometheus_client requests
ENV METRICS_PORT=9101
CMD ["python", "energy_controller.py"]
