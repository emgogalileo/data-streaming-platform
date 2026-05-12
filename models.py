"""
Pydantic domain models for the Data Streaming Platform.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class StreamTopic(BaseModel):
    """Represents a named data stream with its metadata."""

    id: str = Field(..., description="Unique identifier, used in URL paths")
    name: str = Field(..., description="Human-readable topic name")
    unit: str = Field(..., description="Unit of the streamed metric")
    frequency_ms: int = Field(..., description="Approximate emission interval in milliseconds")


class TopicStatus(BaseModel):
    """Runtime stats for a topic."""

    topic_id: str
    total_messages_emitted: int
    last_value: float | None = None
    last_emitted_at: str | None = None


class DataPoint(BaseModel):
    """A single telemetry reading."""

    topic_id: str
    sequence: int
    value: float
    timestamp: str


class MetricSnapshot(BaseModel):
    """A batch of recent data points for a topic."""

    topic_id: str
    count: int
    points: list[DataPoint]
