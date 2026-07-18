"""
Counter service with thread-safe increment operations.

Fixes race condition by using threading.Lock to ensure atomic
increment operations under concurrent requests.
"""

import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Counter Service")

# Shared counter state with thread-safe lock
_counter = 0
_counter_lock = threading.Lock()


class IncrementRequest(BaseModel):
    """Request body for increment endpoint."""
    value: int = 1


class CounterResponse(BaseModel):
    """Response containing the current counter value."""
    count: int


class IncrementResponse(BaseModel):
    """Response after incrementing the counter."""
    previous: int
    current: int


@app.get("/")
def read_root():
    """Root health-check endpoint."""
    return {"status": "ok", "service": "counter"}


@app.get("/counter", response_model=CounterResponse)
def get_counter():
    """Return the current counter value."""
    global _counter
    return CounterResponse(count=_counter)


@app.post("/increment", response_model=IncrementResponse)
def increment(request: IncrementRequest):
    """
    Increment the counter by the given value.

    Uses a threading.Lock to prevent race conditions when
    multiple concurrent requests attempt to increment simultaneously.
    """
    global _counter, _counter_lock

    if request.value < 0:
        raise HTTPException(status_code=400, detail="Increment value must be non-negative")

    with _counter_lock:
        previous = _counter
        _counter += request.value

    return IncrementResponse(previous=previous, current=_counter)
