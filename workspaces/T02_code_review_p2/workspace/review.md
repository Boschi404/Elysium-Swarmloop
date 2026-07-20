---
task: T02_code_review
title: "Memory Leak Pattern — Code Review"
language: "english"
---

# Code Review: Memory Leak Pattern

## 1. Leak Sources Identified

Three distinct memory leak patterns are demonstrated in `leaky_cache.py`:

### Leak A — Unbounded Global Cache Dict

**File:** `leaky_cache.py`, module-level dict `_CACHE`

```python
_CACHE: dict[str, Any] = {}

def get_user_profile(user_id: str) -> dict[str, Any]:
    if user_id not in _CACHE:
        profile = _fetch_from_db(user_id)
        _CACHE[user_id] = profile       # ← never removed
    return _CACHE[user_id]
```

**Why it leaks:**
- The dict `_CACHE` has **no eviction policy**. Every unique key is appended forever.
- In production (real user base) this grows linearly with unique user IDs.
- Each cached value is a ~4 KB dict; after 1M users the cache alone consumes **~4 GB** that can never be freed.
- Because `_CACHE` is a module-level global, it lives for the entire process lifetime.

### Leak B — Orphaned Event Listeners

**File:** `leaky_cache.py`, module-level list `_listeners` + `DataBroadcaster.subscribe()`

```python
_listeners: list[Callable] = []

class DataBroadcaster:
    def subscribe(self, callback):
        _listeners.append(callback)      # ← never removed

class DataConsumer:
    def on_message(self, msg): ...
```

**Why it leaks:**
- `broadcaster.subscribe(c.on_message)` stores a **bound method** (`c.on_message`).
- A bound method holds an implicit strong reference to `self` (the `DataConsumer` instance).
- When the caller drops its reference to `c`, **the global `_listeners` still holds the bound method** → the consumer is never GC'd.
- In a long-running server (e.g., WebSocket handlers, UI controllers) this accumulates every subscriber ever registered, plus every object the subscriber transitively references.

### Leak C — Class-Level Instance Registry

**File:** `leaky_cache.py`, `ExpensiveResource._instances`

```python
class ExpensiveResource:
    _instances: dict[int, ExpensiveResource] = {}

    def __init__(self):
        self.resource_id = ...
        self.data = bytearray(10_000)     # ~10 KB per instance
        _instances[self.resource_id] = self   # ← self-pinning
```

**Why it leaks:**
- Every instance registers itself in a class-level dict.
- The dict holds a strong reference to the instance, and the instance holds a strong reference back to its `data` (and transitively to its class).
- Even when all external references are dropped, the instance is pinned by `_instances` → **uncollectable**.
- If `__del__` is defined, the GC finalization queue can also be affected, but the root cause is the strong ref cycle through the class dict.

---

## 2. Why They Leak (Root-Cause Analysis)

| Leak | Mechanism | Python-Specific Factor |
|------|-----------|------------------------|
| **A** (cache dict) | Strong ref in global dict | Python's GC uses **reference counting + optional cycle detector**. A dict entry is a strong pointer; as long as the dict lives, the value lives. The dict itself is a module-level global → lives for process lifetime. |
| **B** (listeners) | Bound-method strong-ref to `self` | `obj.method` returns a bound method object whose `__self__` is `obj`. The global `_listeners` list holds the method → `obj` lives even with zero external references. |
| **C** (class registry) | Class-level dict has strong ref to instance | Class variables are reachable from the module globals. The `_instances` dict entry is a strong ref to the `ExpensiveResource` instance → the instance is reachable from GC roots → never collected. |

**Common thread:** all three are cases where a **strong reference from a global / long-lived container** holds objects alive that the application considers "done with."

Python's garbage collector cannot reclaim objects that are reachable from roots — and module-level dicts/listings are roots. Leak B and C involve cycles (instance ↔ method ↔ list, instance ↔ class dict ↔ instance), but because the container is a **global reachable root**, even the cycle detector finds them **reachable** and therefore **not garbage**.

---

## 3. Memory Profiling Approach

### 3.1 — Detection via `gc` Module (unit-test level)

```python
import gc

# Force collection of all generations
gc.collect()

# Count objects of a specific type
consumers = [obj for obj in gc.get_objects() if isinstance(obj, DataConsumer)]
print(f"Leaked DataConsumer instances: {len(consumers)}")
```

### 3.2 — Heap snapshot with `tracemalloc`

```python
import tracemalloc

tracemalloc.start()
# ... run operations ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")
for stat in top_stats[:10]:
    print(stat)
```

### 3.3 — Object graph visualization with `objgraph`

```bash
pip install objgraph
```

```python
import objgraph

objgraph.show_refs(
    [leaky_cache._CACHE],
    filename="cache_refs.png",
    refcounts=True,
)
objgraph.show_growth(limit=10)
```

### 3.4 — Production monitoring

| Tool | Use Case |
|------|----------|
| `psutil` | Track RSS / VMS at intervals during load tests |
| `memory_profiler` | Decorator `@profile` on suspect functions |
| `fil-profile` | Peak memory allocation per line (PyPI: `filprofiler`) |
| Prometheus + `gc` collector metrics | Count objects per type every 15 s in Flask/FastAPI middleware |

### 3.5 — Manual "canary" test (demonstrated in accompanying tests)

1. Create N objects
2. Drop all external references
3. Call `gc.collect()`
4. Assert `len([o for o in gc.get_objects() if isinstance(o, Type)]) == 0`

---

## 4. Fixes Applied

### Fix A — LRU Cache via `functools.lru_cache`

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user_profile(user_id: str) -> dict[str, Any]:
    return _fetch_from_db(user_id)
```

**How it fixes the leak:**
- `maxsize=128` bounds the cache → only 128 entries ever live.
- When the 129th unique key is inserted, the **least-recently-used** entry is evicted.
- The decorated function transparently manages a `OrderedDict`-backed cache.

**Trade-off:** when `maxsize` is hit, hot keys may be evicted and need re-fetch. Choose `maxsize` based on workload analysis (peak unique users per time window).

### Fix B — Weak-Referenced Listeners via `weakref.WeakMethod`

```python
import weakref

class WeakListenerSet:
    def add(self, callback):
        ref = weakref.WeakMethod(callback)
        self._refs.append(ref)

    def notify(self, message):
        for ref in list(self._refs):
            cb = ref()
            if cb is not None:
                cb(message)
        self._sweep()  # remove dead refs
```

**How it fixes the leak:**
- `WeakMethod` holds a weak reference to the bound method. When the consumer is dropped, the method is **deallocated** and `ref()` returns `None`.
- The `_sweep()` call after each notification keeps the list compact.

### Fix C — Weak-Referenced Instance Cache via `WeakValueDictionary`

```python
class ExpensiveResourceFixed:
    _instances: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
```

**How it fixes the leak:**
- `WeakValueDictionary` stores values via weak references. When no strong reference to the instance remains, the entry is **automatically removed** at the next GC / dictionary mutation.

---

## 5. Summary

| Leak | Root Cause | Fix | Memory Recovery |
|------|-----------|-----|-----------------|
| Global cache | Unbounded dict | `@lru_cache(maxsize=N)` | Eviction on overflow |
| Event listeners | Bound-method ref in global list | `weakref.WeakMethod` | GC when subscriber drops out of scope |
| Instance registry | Class dict self-reference | `WeakValueDictionary` | GC when last external ref drops |

**Defense in depth:**
- Always size caches (LRU / TTL / size-bound).
- Prefer weak references for observer / listener / callback patterns.
- Use `gc` and `tracemalloc` in CI to catch regressions.
- Monitor object counts per type in production.
