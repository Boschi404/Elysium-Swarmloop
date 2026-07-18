# T02_code_review — Memory Leak Pattern: Review Report

**Reviewer:** Hermes Agent (Elysium Swarmloop)  
**File:** `code_with_leak.py`  
**Date:** 2026-07-18

---

## 1. Leak Source A — Unbounded Global Cache

### Location
`_RESULT_CACHE: dict[str, Any]` (module-level)  
`ExpensiveComputation.compute()` — line that stores: `_RESULT_CACHE[key] = result`

### Why It Leaks

- The cache is a **global dict** with no eviction policy, no size limit, and no TTL.
- Every unique `key` argument ever passed to `compute()` appends a new entry forever.
- In a long-running process (server, daemon, desktop app) the cache grows monotonically until it exhausts the available heap.
- The dict holds **strong references** to every result object — nothing short of an explicit `del` or a process restart can reclaim them.

### Impact
- **Memory:** O(N) where N = number of unique keys seen over the process lifetime.
- **Performance:** dict lookup stays O(1), but the GC mark-and-sweep cost grows with every retained object.
- **Production scenario:** A web API that caches per-user query results — after one week the cache holds millions of entries and the process OOMs.

---

## 2. Leak Source B — Event Listeners Never Removed

### Location
`EventEmitter._listeners: dict[str, list[Callable]]`  
`EventEmitter.on()` — appends callback without ever providing a `disconnect` / `remove` / `off` method.

### Why It Leaks

- The emitter stores **strong references** to every callback.
- Each callback's **closure** captures `sink` (DataSink) and `payload` (LargePayload, ~1 MB each).
- Even after the caller discards its own reference to those objects, the closure keeps them alive because the emitter's listener list owns a strong reference to the closure.
- Result: **100 MB+ retained** that the developer thinks is freed.

### The Closure Trap

```python
def make_cb(s=sink, p=payload):
    def cb(value):
        s.on_data(value)
        _ = len(p.payload)    # keeps p alive
    return cb
```

`cb.__closure__` holds `cell` objects referencing `s` and `p`. Since `cb` is stored by strong reference in `emitter._listeners`, neither `sink` nor the 1 MB `LargePayload` can be garbage-collected — even after the calling scope is long gone.

### Impact
- **Memory:** Each listener chain holds potentially megabytes of referenced objects alive.
- **Correctness:** After 10,000 `on("update", ...)` calls, emitting "update" iterates 10,000 callbacks — O(N) slowdown AND O(N) memory.
- **Production scenario:** A chat application that registers a listener for every opened tab — closing the tab does not clean up, and after 500 tabs the listener list contains 500 dead entries all referencing discarded UI state.

---

## 3. Memory Profiling Approach

### Recommended tools and methodology

#### a) Heap snapshot diff (pympler / tracemalloc)

```python
# Install: pip install pympler
from pympler import muppy, summary
from pympler.classtracker import ClassTracker

tracker = ClassTracker()
tracker.track_object(emitter)
tracker.track_object(ExpensiveComputation)

# After running workload
summary.print_(summary.summarize(muppy.get_objects()))
```

Look for:
- `LargePayload` instances count > expected (each listener closure references one)
- `DataSink` instances retained after the caller dropped its list

#### b) `tracemalloc` (stdlib, Python 3.4+)

```python
import tracemalloc
tracemalloc.start()

# ... run workload ...
snapshot = tracemalloc.take_snapshot()
stats = snapshot.statistics('lineno')
for stat in stats[:10]:
    print(stat)
```

Filter by `code_with_leak.py` to see which line allocates the most.

#### c) GC inspection

```bash
python -c "
import gc
# After workload, before & after gc.collect()
unreachable = gc.collect()
print(f'Unreachable objects: {unreachable}')
# Objects still alive
for obj in gc.get_objects():
    if isinstance(obj, ...):
        gc.get_referrers(obj)   # what keeps it alive?
"
```

The key question to ask: **"Who still references this object?"** — `gc.get_referrers()` tells you.

#### d) Valgrind / `memray` (C-level)

```bash
pip install memray
python -m memray run code_with_leak.py
python -m memray flamegraph memray-output.bin
```

Shows native-level allocations — useful when the leak is in a C extension (e.g., numpy array held by closure).

### Profiling checklist

| Technique | Finds | Difficulty |
|-----------|-------|------------|
| `pympler` tracker | Python object counts per class | Easy |
| `tracemalloc` | Line-level allocation hot-spots | Easy |
| `gc.get_referrers()` | Reference chains (who holds whom alive) | Medium |
| `memray` | Native/C-level allocations | Advanced |

---

## 4. Fix Strategy (implemented in `code_fixed.py`)

### Fix 1 — LRU Cache (`functools.lru_cache`)

Replace the unbounded dict with `functools.lru_cache(maxsize=128)`:

```python
@staticmethod
@functools.lru_cache(maxsize=128)
def compute(key: str, /) -> frozenset:
    ...
```

**Properties:**
- **Bounded:** max 128 entries. When full, the LEAST RECENTLY USED entry is evicted.
- **Thread-safe:** built-in locking.
- **Introspectable:** `compute.cache_info()` returns hits, misses, current size.
- **Alternative:** `@cachetools.LRUCache(maxsize=1024)` if you need custom TTL.

**Why LRU fits this pattern:** Computations have temporal locality — recently-used results are likely to be reused. The 128 newest entries cover the working set without growing unboundedly.

### Fix 2 — Weak References + Explicit Disconnect

Replace strong `list[Callable]` with `list[weakref.ref]` and provide a `disconnect()` method:

```python
class WeakEventEmitter:
    def on(self, event, callback):
        self._listeners[event].append(weakref.ref(callback))
        return CleanupHandle(self, event, callback)

    def emit(self, event, **kwargs):
        alive = []
        for ref in self._listeners.get(event, []):
            cb = ref()
            if cb is not None:
                cb(**kwargs)
                alive.append(ref)
        self._listeners[event] = alive   # auto-prune dead refs

    def disconnect(self, event, callback):
        ... # remove matching callback
```

**Properties:**
- Listeners held by weakref → garbage collector can reclaim the callback + its closure.
- Dead weakrefs are silently dropped on the next `emit()`.
- The caller can also proactively `disconnect()` using the returned handle.

### Combined effect

| Pattern | Before | After |
|---------|--------|-------|
| Cache | Unbounded dict | `lru_cache(maxsize=128)` |
| Listeners | Strong ref, no cleanup | `weakref.ref` + `disconnect()` |
| Memory | Grows monotonically | Bounded + self-cleaning |
| Thread-safety | None | Built-in for cache; emit is O(n) |

---

## 5. Prevention (organizational)

1. **Code review checklist item:** "Does this cache have an eviction policy?"
2. **Linting:** Add a flake8 plugin or custom grep for module-level mutable collections.
3. **Leak regression test:** `test_memory_leak.py` that runs the component, forces GC, and asserts object count stays constant.
4. **Production monitoring:** Report `lru_cache.currsize` as a Prometheus metric. Alert on unbounded growth of any custom cache.

---

*Report generated as part of T02_code_review solution set.*
