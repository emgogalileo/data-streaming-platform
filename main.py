"""
Data Streaming Platform — FastAPI Backend
==========================================
Simulates a real-time telemetry data stream over Server-Sent Events (SSE)
and exposes a REST API for stream control and metric queries.

Architecture:
    Client ──SSE──▶  /api/stream/{topic}
    Client ──REST──▶ /api/metrics, /api/topics

Dependencies:
    pip install fastapi uvicorn python-dotenv

Run:
    uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

import asyncio
import json
import random
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from models import MetricSnapshot, StreamTopic, TopicStatus
from services.generator import DataGenerator


# ── Application factory ────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:  # type: ignore[type-arg]
    """Startup / shutdown lifecycle hook."""
    print("🚀  Data Streaming Platform starting…")
    yield
    print("🛑  Data Streaming Platform shutting down.")


app = FastAPI(
    title="Data Streaming Platform",
    description="Real-time telemetry data streaming API with SSE.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow all origins in dev; restrict in production via env
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

generator = DataGenerator()

# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/api/health", tags=["meta"])
def health_check() -> dict:
    """Liveness probe endpoint."""
    return {
        "status": "ok",
        "service": "data-streaming-platform",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── Topics ─────────────────────────────────────────────────────────────────────

AVAILABLE_TOPICS: list[StreamTopic] = [
    StreamTopic(id="iot-sensors", name="IoT Sensors", unit="°C / % / lx", frequency_ms=500),
    StreamTopic(id="stock-prices", name="Stock Prices", unit="USD", frequency_ms=1000),
    StreamTopic(id="network-traffic", name="Network Traffic", unit="Mbps", frequency_ms=750),
    StreamTopic(id="cpu-usage", name="CPU Usage", unit="%", frequency_ms=500),
]


@app.get("/api/topics", response_model=list[StreamTopic], tags=["topics"])
def list_topics() -> list[StreamTopic]:
    """Return all available stream topics."""
    return AVAILABLE_TOPICS


@app.get("/api/topics/{topic_id}/status", response_model=TopicStatus, tags=["topics"])
def topic_status(topic_id: str) -> TopicStatus:
    """Return the current status of a topic (active subscribers, message count)."""
    topic = next((t for t in AVAILABLE_TOPICS if t.id == topic_id), None)
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_id}' not found.")
    return generator.get_topic_status(topic_id)


# ── Metrics snapshot ───────────────────────────────────────────────────────────

@app.get("/api/metrics/{topic_id}", response_model=MetricSnapshot, tags=["metrics"])
def get_metrics_snapshot(topic_id: str, n: int = 10) -> MetricSnapshot:
    """
    Return the last *n* data points for a topic without subscribing to the stream.
    """
    topic = next((t for t in AVAILABLE_TOPICS if t.id == topic_id), None)
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_id}' not found.")
    return generator.snapshot(topic_id, n)


# ── SSE Stream ─────────────────────────────────────────────────────────────────

async def _event_generator(topic_id: str, interval_s: float) -> AsyncGenerator[str, None]:
    """
    Async generator that emits Server-Sent Event formatted strings.
    Each event is a JSON-encoded data point.
    """
    sequence = 0
    while True:
        point = generator.generate_point(topic_id, sequence)
        payload = json.dumps(point)
        # SSE format: "data: <json>\n\n"
        yield f"data: {payload}\n\n"
        sequence += 1
        await asyncio.sleep(interval_s)


@app.get("/api/stream/{topic_id}", tags=["stream"])
def stream_topic(topic_id: str) -> StreamingResponse:
    """
    Open a Server-Sent Events stream for the given topic.

    Connect with EventSource in JavaScript:
        const es = new EventSource('/api/stream/cpu-usage');
        es.onmessage = (e) => console.log(JSON.parse(e.data));
    """
    topic = next((t for t in AVAILABLE_TOPICS if t.id == topic_id), None)
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_id}' not found.")

    interval_s = topic.frequency_ms / 1000
    return StreamingResponse(
        _event_generator(topic_id, interval_s),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable Nginx buffering
        },
    )
