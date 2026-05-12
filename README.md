# Data Streaming Platform

Real-time telemetry streaming API built with **Python** and **FastAPI**, using Server-Sent Events (SSE).

## Tech Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI 0.115+
- **Transport**: Server-Sent Events (SSE)
- **Data**: Pydantic v2 models with random-walk simulation

## Getting Started

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs` (Swagger UI).

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Service health check |
| `GET` | `/api/topics` | List all stream topics |
| `GET` | `/api/topics/{id}/status` | Topic runtime stats |
| `GET` | `/api/metrics/{id}?n=10` | Last N data points snapshot |
| `GET` | `/api/stream/{id}` | Open SSE stream (text/event-stream) |

## Available Topics

| ID | Name | Unit |
|----|------|------|
| `iot-sensors` | IoT Sensors | °C / % / lx |
| `stock-prices` | Stock Prices | USD |
| `network-traffic` | Network Traffic | Mbps |
| `cpu-usage` | CPU Usage | % |

## Connecting from JavaScript

```js
const es = new EventSource('http://localhost:8000/api/stream/cpu-usage');
es.onmessage = (e) => {
  const point = JSON.parse(e.data);
  console.log(point.value, point.timestamp);
};
```

## Project Structure

```
├── main.py            # FastAPI app & routes
├── models.py          # Pydantic data models
├── services/
│   └── generator.py   # Synthetic data generator (random walk)
└── requirements.txt
```

## Author
Emmanuel García — [emmanuelg@allcognition.com](mailto:emmanuelg@allcognition.com)
