# app.py
from fastapi import FastAPI
import random, time
from prometheus_client import start_http_server, Gauge
import uvicorn

app = FastAPI(title="Green AI Service")

carbon_intensity = Gauge('carbon_intensity', 'Current carbon intensity (gCO2/kWh)')
renewable_share  = Gauge('renewable_share', 'Share of renewable energy (0–1)')
green_score      = Gauge('green_score', 'Normalized green score (0–1)')

@app.get("/v1/energy/now")
def get_energy_now():
    carbon = random.uniform(200, 600)
    renew  = random.uniform(0.2, 0.9)
    score  = 1 - (carbon/600)*0.5 + renew*0.5
    carbon_intensity.set(carbon)
    renewable_share.set(renew)
    green_score.set(score)
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "carbon_intensity": round(carbon, 2),
        "renewable_share": round(renew, 2),
        "green_score": round(score, 2)
    }

if __name__ == "__main__":
    start_http_server(8001)   # metrics endpoint
    uvicorn.run(app, host="0.0.0.0", port=8000)
