"""
T02 Bug Fixing — Counter Service with Race Condition Fix

Race condition identified:
- Global `counter` variable is read-increment-write without synchronisation.
- Under concurrent load, two requests can read the same value, increment locally,
  and write back — losing one of the increments (classic read-modify-write race).

Fix applied:
- `asyncio.Lock` ensures mutual exclusion on both increment and read operations,
  making the counter thread-safe for asynchronous concurrency.
"""

import asyncio
from fastapi import FastAPI

app = FastAPI(title="Counter Service", version="1.0.0")

# ── Shared state with synchronisation ──────────────────────────────
_counter: int = 0
_lock: asyncio.Lock = asyncio.Lock()


@app.post("/increment")
async def increment():
    """Atomically increment the counter and return the new value."""
    global _counter
    async with _lock:
        _counter += 1
        return {"counter": _counter}


@app.get("/counter")
async def get_counter():
    """Return the current counter value (thread-safe read)."""
    global _counter
    async with _lock:
        return {"counter": _counter}
