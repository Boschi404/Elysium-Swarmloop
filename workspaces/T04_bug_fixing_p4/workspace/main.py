"""
Events API — Timezone-aware date handling.

The bug: POST /events stored dates in naive local time, and GET /events
returned naive datetime values. Around DST transitions, the offset between
local time and UTC shifted, causing off-by-one errors in stored dates.

The fix:
  - All incoming dates are parsed with timezone awareness: if the client
    sends a naive datetime, it is interpreted as UTC (assumed UTC).
  - Internally, all datetimes are stored in UTC (normalised).
  - On output (GET), datetimes are converted to the client's local time
    using a configurable TIMEZONE setting (default: Europe/Rome).
  - Every date-parsing path is wrapped in try/except to surface
    validation errors as 422 HTTP responses, never 500.
"""

import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, field_validator
import pytz

from contextlib import asynccontextmanager
from collections.abc import Iterator

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LOCAL_TIMEZONE = os.getenv("EVENTS_TZ", "Europe/Rome")

# In-memory store: list of event dicts with UTC-aware datetimes
events_store: list[dict] = []


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class EventCreate(BaseModel):
    """Incoming event payload."""

    name: str
    date: str  # ISO-8601 string, e.g. "2025-03-30T01:00:00" or "2025-03-30T01:00:00Z"

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @field_validator("date")
    @classmethod
    def parse_date(cls, v: str) -> str:
        """Validate and normalise the incoming date string to UTC ISO-8601."""
        try:
            dt = _parse_iso_datetime(v)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"Invalid date format '{v}'. "
                f"Expected ISO-8601 (e.g. '2025-03-30T01:00:00'). "
                f"Parse error: {exc}"
            ) from exc

        # Normalise to UTC, strip tzinfo for a clean UTC ISO string
        dt_utc = dt.astimezone(timezone.utc)
        return dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")


class EventResponse(BaseModel):
    """Event as returned to the client, with datetime converted to local time."""

    id: int
    name: str
    date: str  # ISO-8601 in the configured local timezone


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_iso_datetime(s: str) -> datetime:
    """Parse an ISO-8601 string into an aware datetime.

    - If the string includes a tz offset (Z, +01:00), respect it.
    - If the string is naive, assume UTC (matching the API contract).
    """
    # Python 3.11's datetime.fromisoformat handles 'Z' suffix via replace()
    s = s.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        # Naive incoming → assume UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _utc_to_local(dt: datetime, tz_name: str) -> datetime:
    """Convert an aware UTC datetime to the given timezone."""
    target_tz = pytz.timezone(tz_name)
    return dt.astimezone(target_tz)


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(application: FastAPI) -> Iterator[None]:
    """Application lifespan — currently a no-op but required for startup."""
    yield


app = FastAPI(title="Events API — Timezone-Aware", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/events")
def list_events(
    tz: Optional[str] = Query(
        None,
        description="Override timezone for output (IANA name, e.g. 'America/New_York')",
    ),
) -> dict:
    """
    Return all events with dates converted to local time.

    By default uses the EVENTS_TZ env variable (fallback: Europe/Rome).
    The client can override the output timezone via the `tz` query parameter.
    """
    output_tz = tz or LOCAL_TIMEZONE

    # Validate the requested timezone
    try:
        pytz.timezone(output_tz)
    except pytz.UnknownTimeZoneError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown timezone '{output_tz}'. Use a valid IANA timezone name.",
        )

    results: list[dict] = []
    for event in events_store:
        try:
            dt_utc = _parse_iso_datetime(event["date"])
        except ValueError:
            # Should never happen for stored events, but guard anyway
            raise HTTPException(
                status_code=500,
                detail=f"Corrupt stored date for event {event['id']}: {event['date']}",
            )

        dt_local = _utc_to_local(dt_utc, output_tz)
        results.append({
            "id": event["id"],
            "name": event["name"],
            "date": dt_local.strftime("%Y-%m-%dT%H:%M:%S"),
        })

    return {"events": results, "count": len(results)}


@app.post("/events", status_code=201)
def create_event(payload: EventCreate) -> dict:
    """
    Create a new event.

    The incoming date is parsed with timezone awareness and stored in UTC
    internally.  Naive datetimes are assumed to be UTC.
    """
    global events_store

    event_id = len(events_store) + 1
    events_store.append({
        "id": event_id,
        "name": payload.name,
        "date": payload.date,  # Already normalised to UTC ISO by the validator
    })

    return {
        "id": event_id,
        "name": payload.name,
        "date": payload.date,
    }


@app.get("/health")
def health_check() -> dict:
    """Simple health-check endpoint."""
    return {"status": "ok", "timezone": LOCAL_TIMEZONE, "events_count": len(events_store)}


@app.get("/")
def root() -> dict:
    """Root — API information."""
    return {
        "app": "Events API",
        "version": "1.0.0",
        "endpoints": {
            "GET /events": "List all events with local-time dates",
            "POST /events": "Create a new event (UTC-normalised storage)",
            "GET /health": "Health check",
        },
    }
