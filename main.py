from fastapi import FastAPI, BackgroundTasks
import asyncio
import random
from typing import List, Dict

app = FastAPI(title="Data Streaming Analytics")

data_stream: List[Dict] = []

def generate_stream_data():
    return {
        "device_id": f"dev_{random.randint(100, 999)}",
        "temperature": round(random.uniform(20.0, 80.0), 2),
        "status": random.choice(["active", "idle", "maintenance"]),
        "throughput_mbps": round(random.uniform(10.0, 1000.0), 2)
    }

async def stream_worker():
    while True:
        if len(data_stream) > 100:
            data_stream.pop(0)
        data_stream.append(generate_stream_data())
        await asyncio.sleep(2)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(stream_worker())

@app.get("/api/stream/latest")
async def get_latest_data():
    if not data_stream:
        return {"status": "waiting for data"}
    return {"latest": data_stream[-1]}

@app.get("/api/stream/history")
async def get_history_data():
    return {"history": data_stream[-10:]}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Data Streaming Analytics API"}
