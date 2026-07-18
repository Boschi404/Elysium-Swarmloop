"""
Counter Service with Thread-Safe Operations.

Provides a FastAPI application that maintains a counter with thread-safe
increment operations, preventing race conditions from concurrent requests.
"""

import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class Counter:
    """A thread-safe counter using a lock to prevent race conditions."""

    def __init__(self) -> None:
        self._value: int = 0
        self._lock: threading.Lock = threading.Lock()

    def increment(self) -> int:
        """Increment the counter by 1 and return the new value.

        Uses a threading.Lock to ensure the read-modify-write cycle is atomic.
        """
        with self._lock:
            self._value += 1
            return self._value

    def value(self) -> int:
        """Return the current counter value.

        Read access is also locked to guarantee visibility across threads.
        """
        with self._lock:
            return self._value

    def reset(self) -> None:
        """Reset the counter to zero (for testing purposes)."""
        with self._lock:
            self._value = 0


_counter = Counter()
app = FastAPI(title="Counter Service", version="1.0.0")


class IncrementResponse(BaseModel):
    """Response model for the increment endpoint."""
    count: int


class CounterResponse(BaseModel):
    """Response model for the counter read endpoint."""
    count: int


class ErrorResponse(BaseModel):
    """Response model for error cases."""
    detail: str


@app.get("/counter", response_model=CounterResponse)
async def get_counter() -> CounterResponse:
    """Return the current counter value."""
    return CounterResponse(count=_counter.value())


@app.post("/increment", response_model=IncrementResponse)
async def increment_counter() -> IncrementResponse:
    """Increment the counter and return the new value.

    This operation is thread-safe: concurrent requests do not lose counts.
    """
    new_value = _counter.increment()
    return IncrementResponse(count=new_value)


@app.post("/counter/reset")
async def reset_counter() -> CounterResponse:
    """Reset the counter to zero (useful for testing)."""
    _counter.reset()
    return CounterResponse(count=0)
