"""
Counter Service — Thread-Safe Increment API

A FastAPI counter service that handles concurrent POST /increment requests
without losing counts, using a threading.Lock for atomic operations.
"""

import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Counter Service")

# Shared counter state with thread-safe lock
_counter: int = 0
_lock = threading.Lock()


class IncrementResponse(BaseModel):
    """Response model for increment operations."""
    counter: int
    message: str


class CounterResponse(BaseModel):
    """Response model for counter queries."""
    counter: int


@app.get("/counter", response_model=CounterResponse)
def get_counter():
    """Return the current counter value."""
    with _lock:
        return CounterResponse(counter=_counter)


@app.post("/increment", response_model=IncrementResponse)
def increment():
    """
    Increment the counter by 1 in a thread-safe manner.

    Uses threading.Lock to ensure atomic read-modify-write,
    preventing lost updates under concurrent requests.
    """
    try:
        with _lock:
            global _counter
            _counter += 1
            current = _counter
        return IncrementResponse(counter=current, message="Counter incremented")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Increment failed: {str(e)}")
