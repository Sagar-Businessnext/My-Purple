# Common Python Pitfalls

## 1. Mutable Default Arguments

**The bug:** Python evaluates default argument values once at function definition time, not each call. A mutable default is shared across all calls.

```python
# WRONG — all callers share the same list object
def add_item(item: str, items: list[str] = []) -> list[str]:
    items.append(item)
    return items

add_item("a")  # ["a"]
add_item("b")  # ["a", "b"]  ← unexpected! not a fresh list

# CORRECT — use None sentinel, initialize inside the function
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

## 2. Swallowed Exceptions

**The bug:** A bare `except` or `except Exception` with `pass` hides failures silently. The service appears to work but produces wrong results or does nothing.

```python
# WRONG — silent failure
def get_config_value(key: str) -> str | None:
    try:
        return os.environ[key]
    except Exception:
        pass  # caller has no idea the key was missing

# CORRECT — log and return a meaningful default, or re-raise
import logging
logger = logging.getLogger(__name__)

def get_config_value(key: str) -> str | None:
    try:
        return os.environ[key]
    except KeyError:
        logger.warning("Config key %s not found", key)
        return None
```

## 3. List Comprehension with Side Effects

**The bug:** Side effects inside comprehensions are hard to see and execute in an order that may surprise readers.

```python
# WRONG — side effect (print) buried in comprehension
processed = [process_and_log(item) for item in items]  # if process_and_log has side effects

# CORRECT — explicit loop makes the side effect visible
processed = []
for item in items:
    result = process(item)
    logger.info("Processed item %s -> %s", item, result)
    processed.append(result)
```

## 4. Using `list()` Where a Generator Suffices

```python
# WRONG — materializes entire list just to check membership
if target in list(generate_candidates()):  # list is never used as a list
    ...

# CORRECT — generator short-circuits on first match
if target in generate_candidates():
    ...

# WRONG — wrapping a generator expression in a list for sum/any/all
total = sum([x * 2 for x in items])  # list is unnecessary

# CORRECT — generator expression
total = sum(x * 2 for x in items)
```

## 5. Catching Too Broadly and Masking the Real Error

```python
# WRONG — catches everything including KeyboardInterrupt, SystemExit
try:
    result = risky_operation()
except Exception as e:
    logger.error("Something went wrong")  # no context, no re-raise, no type info

# CORRECT — catch the specific exception you can handle
try:
    result = risky_operation()
except ValueError as e:
    logger.error("Invalid input to risky_operation: %s", e)
    raise
except httpx.TimeoutException:
    logger.warning("Timeout calling external service; using cached value")
    result = CACHED_FALLBACK
```

## 6. Integer vs Float Division

```python
# WRONG in Python 3 — looks like integer division but is float
pages = total_items / page_size   # 10 / 3 = 3.3333... not 3

# CORRECT — use // for integer (floor) division
pages = total_items // page_size  # 10 // 3 = 3

# Or be explicit about ceiling division
import math
pages = math.ceil(total_items / page_size)
```

## 7. Late Binding in Closures

```python
# WRONG — all lambdas reference the same `i` variable (last value = 9)
funcs = [lambda: i for i in range(10)]
funcs[0]()  # returns 9, not 0

# CORRECT — bind the current value with a default argument
funcs = [lambda i=i: i for i in range(10)]
funcs[0]()  # returns 0
```

## 8. Walrus Operator Overuse

The walrus operator (`:=`) is useful for `while` loops and avoiding double evaluation. It becomes a readability issue in nested comprehensions.

```python
# GOOD — standard pattern for chunked reading
with open("large_file.bin", "rb") as f:
    while chunk := f.read(8192):
        process(chunk)

# ACCEPTABLE — avoids calling expensive function twice
if result := compute_expensive():
    use(result)

# BAD — two nested walrus operators in a comprehension
results = [y for x in data if (z := transform(x)) if (y := filter(z))]
# Just write a loop.
```
