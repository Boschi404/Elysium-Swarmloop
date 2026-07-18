"""
Events API — Timezone-Aware Date Handling

Bug: POST /events stored dates without timezone information, and GET /events
returned them in local time inconsistently, causing off-by-one errors around
DST transitions.

Fix: 
- Parse all incoming dates as timezone-aware (assume UTC if none provided)
- Store all dates internally as timezone-aware UTC
- Return all dates in ISO-8601 format with explicit UTC marker
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, field_validator
import pytz

app = FastAPI(title="Events API", version="1.0.0")

# In-memory event store
events_db: list[dict] = []
_id_counter: int = 0


def _parse_utc(date_str: str) -> datetime:
    """Parse a date string into a timezone-aware UTC datetime.

    Handles:
    - ISO-8601 with explicit timezone (e.g. '2024-03-31T02:00:00+02:00')
    - ISO-8601 with Z suffix (e.g. '2024-03-31T00:00:00Z')
    - Naive date-only (e.g. '2024-03-31') — assumed UTC
    - Naive datetime (e.g. '2024-03-31T00:00:00') — assumed UTC
    """
    try:
        dt = datetime.fromisoformat(date_str)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format: '{date_str}'. Use ISO-8601 format.",
        ) from exc

    if dt.tzinfo is None:
        # Naive datetime — assume UTC
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        # Convert everything to UTC
        dt = dt.astimezone(timezone.utc)
    return dt


def _format_utc(dt: datetime) -> str:
    """Format a timezone-aware datetime as ISO-8601 with UTC offset."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


# ── Pydantic models ──────────────────────────────────────────────────────────


class EventCreate(BaseModel):
    """Request body for creating an event."""

    title: str
    date: str  # ISO-8601 date string

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("title must not be empty")
        return stripped

    @field_validator("date")
    @classmethod
    def date_must_be_valid(cls, v: str) -> str:
        """Validate the date string can be parsed before storing."""
        _parse_utc(v)
        return v


class EventOut(BaseModel):
    """Response body for an event — dates are always UTC."""

    id: int
    title: str
    date: str  # ISO-8601 string, always with UTC offset


# ── API routes ───────────────────────────────────────────────────────────────


@app.post("/events", status_code=201, response_model=EventOut)
def create_event(event: EventCreate):
    """Create a new event.  The date is stored internally as UTC."""
    global _id_counter
    _id_counter += 1

    parsed = _parse_utc(event.date)

    record = {
        "id": _id_counter,
        "title": event.title,
        "date": parsed,  # timezone-aware UTC datetime
    }
    events_db.append(record)

    return EventOut(
        id=record["id"],
        title=record["title"],
        date=_format_utc(record["date"]),
    )


@app.get("/events", response_model=list[EventOut])
def list_events(
    title: Optional[str] = Query(None, description="Filter by title (substring match)"),
):
    """List all events.  All dates are returned in UTC."""
    if title:
        filtered = [e for e in events_db if title.lower() in e["title"].lower()]
    else:
        filtered = list(events_db)

    return [
        EventOut(
            id=e["id"],
            title=e["title"],
            date=_format_utc(e["date"]),
        )
        for e in filtered
    ]


@app.get("/events/{event_id}", response_model=EventOut)
def get_event(event_id: int):
    """Get a single event by ID."""
    for e in events_db:
        if e["id"] == event_id:
            return EventOut(
                id=e["id"],
                title=e["title"],
                date=_format_utc(e["date"]),
            )
    raise HTTPException(status_code=404, detail=f"Event {event_id} not found")


@app.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: int):
    """Delete an event by ID."""
    for i, e in enumerate(events_db):
        if e["id"] == event_id:
            events_db.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Event {event_id} not found")


@app.get("/")
def root():
    return {"status": "ok", "message": "Events API — timezone-aware"}
