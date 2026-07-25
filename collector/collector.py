# collector/collector.py
from prometheus_client import Gauge, start_http_server
import time, os, requests

EM_KEY = os.getenv('ELECTRICITYMAP_KEY', '')
OWM_KEY = os.getenv('OPENWEATHERMAP_KEY', '')

renewable_gauge = Gauge('region_renewable_percent', 'Renewable percent for region', ['region'])

def fetch_electricitymap(region_code):
    # placeholder: implement actual API call
    # return percent 0-100
    return 42.0

def loop():
    start_http_server(8000)
    regions = os.getenv('REGIONS','node_a_germany,node_b_france,node_c_spain').split(',')
    while True:
        for r in regions:
            percent = fetch_electricitymap(r)
            renewable_gauge.labels(region=r).set(percent)
        time.sleep(300)  # every 5 minutes

if __name__ == "__main__":
    loop()
