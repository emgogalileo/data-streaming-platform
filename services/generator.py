"""
Data generator service — produces realistic synthetic telemetry.

Design:
  - Configurable per-topic ranges and noise profiles.
  - Keeps an in-memory circular buffer (maxlen=1000) per topic.
  - Stateless from the API's perspective; inject as a singleton.
"""

from __future__ import annotations

import random
from collections import deque
from datetime import datetime, timezone
from typing import Any

from models import DataPoint, MetricSnapshot, TopicStatus


# Topic configuration: min, max, baseline, noise_std
_TOPIC_CONFIG: dict[str, dict[str, float]] = {
    "iot-sensors": {"min": 15.0, "max": 45.0, "baseline": 25.0, "noise": 1.5},
    "stock-prices": {"min": 100.0, "max": 500.0, "baseline": 250.0, "noise": 8.0},
    "network-traffic": {"min": 0.0, "max": 1000.0, "baseline": 300.0, "noise": 50.0},
    "cpu-usage": {"min": 0.0, "max": 100.0, "baseline": 45.0, "noise": 10.0},
}


class DataGenerator:
    """
    Generates synthetic time-series data for registered topics.

    Each topic has a random-walk baseline to simulate realistic
    sensor drift rather than pure white noise.
    """

    def __init__(self, buffer_size: int = 1000) -> None:
        self._buffers: dict[str, deque[DataPoint]] = {
            topic: deque(maxlen=buffer_size) for topic in _TOPIC_CONFIG
        }
        self._counters: dict[str, int] = {topic: 0 for topic in _TOPIC_CONFIG}
        self._current_values: dict[str, float] = {
            cfg_key: cfg["baseline"] for cfg_key, cfg in _TOPIC_CONFIG.items()
        }

    def generate_point(self, topic_id: str, sequence: int) -> dict[str, Any]:
        """
        Generate a single data point with a random walk.
        Returns a plain dict suitable for JSON serialisation.
        """
        cfg = _TOPIC_CONFIG.get(topic_id, _TOPIC_CONFIG["cpu-usage"])

        # Random walk: small Gaussian step from current value
        delta = random.gauss(0, cfg["noise"])
        new_value = self._current_values.get(topic_id, cfg["baseline"]) + delta
        new_value = max(cfg["min"], min(cfg["max"], new_value))  # clamp
        self._current_values[topic_id] = new_value

        point = DataPoint(
            topic_id=topic_id,
            sequence=sequence,
            value=round(new_value, 3),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        if topic_id in self._buffers:
            self._buffers[topic_id].append(point)
            self._counters[topic_id] += 1

        return point.model_dump()

    def snapshot(self, topic_id: str, n: int = 10) -> MetricSnapshot:
        """Return the last *n* buffered points for a topic."""
        buf = self._buffers.get(topic_id, deque())
        recent = list(buf)[-n:]
        return MetricSnapshot(topic_id=topic_id, count=len(recent), points=recent)

    def get_topic_status(self, topic_id: str) -> TopicStatus:
        """Return runtime stats for a topic."""
        buf = self._buffers.get(topic_id, deque())
        last = buf[-1] if buf else None
        return TopicStatus(
            topic_id=topic_id,
            total_messages_emitted=self._counters.get(topic_id, 0),
            last_value=last.value if last else None,
            last_emitted_at=last.timestamp if last else None,
        )
