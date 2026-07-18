"""Counter Service — Thread-safe counter with FastAPI.

Fixes the race condition in the original counter implementation:
- Uses threading.Lock to serialise concurrent POST /increment requests
- Atomic read-modify-write cycle prevents lost updates
- Both GET and POST are protected by the same lock
"""

import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Counter Service")

# Shared counter state protected by a reentrant lock
_counter: int = 0
_lock = threading.Lock()


class CounterResponse(BaseModel):
    count: int


class IncrementResponse(BaseModel):
    count: int
    incremented: bool


@app.get("/counter", response_model=CounterResponse)
def get_counter():
    """Return the current counter value."""
    try:
        with _lock:
            return CounterResponse(count=_counter)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/increment", response_model=IncrementResponse)
def increment_counter():
    """Atomically increment the counter by 1.

    The threading.Lock ensures that concurrent requests do not
    interleave the read-modify-write sequence, preventing lost updates.
    """
    global _counter
    try:
        with _lock:
            _counter += 1
            return IncrementResponse(count=_counter, incremented=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
