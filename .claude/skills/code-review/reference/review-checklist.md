# Code Review Checklist — General Purpose (any stack)

Use this checklist when reviewing any code, regardless of stack. Run the **Universal** sections first, then the **Stack-specific overlay** for whichever language(s) the project uses.

If the project has a profile-specific reviewer (e.g., `react-code-verifier`), prefer that over this generic checklist for files inside that profile's scope. This file is the fallback for any stack not covered by a profile reviewer and the default for cross-stack monorepos.

---

## Part 1 — Universal checks

These categories apply to any language. Each row maps to one of the **category vocabulary** labels listed at the end — use those exact labels in the report's `Category` column.

### 1.1 Correctness

| Check | Severity if violated |
|---|---|
| Logic is correct — no off-by-one, no wrong operators (`&&`/`||`, `==`/`===`, `=`/`==`) | CRITICAL |
| Loop bounds correct — no swapped start/end, no underflow | CRITICAL |
| Async operations awaited — no fire-and-forget promises / tasks / futures | CRITICAL |
| Return values used — no ignored return that signals an error | CRITICAL |
| Edge cases considered — empty arrays, zero, negative, max/min, missing keys, blank strings | WARNING |
| Date / time math correct — no naive UTC/local mix, no DST assumptions, no integer-overflow on epoch math | WARNING |
| Concurrency safety — no torn reads, no double-init, no shared-mutable across threads/coroutines without sync | CRITICAL |
| Resource handling — file / connection / lock released on every path | CRITICAL |

### 1.2 Security

| Check | Severity if violated |
|---|---|
| No SQL string concatenation — use parameterized queries / prepared statements / ORM bind | CRITICAL |
| No user input in HTML / templates without escaping — XSS | CRITICAL |
| No command-line built from user input — command injection | CRITICAL |
| No path built from user input without normalization + allow-list — path traversal | CRITICAL |
| No `eval` / `new Function` / `exec` of user input — code injection | CRITICAL |
| No unsafe deserialization of untrusted input (pickle, ObjectInputStream, BinaryFormatter) | CRITICAL |
| No secrets in source — API keys, passwords, tokens, connection strings, private keys | CRITICAL |
| Auth/authz enforced at every endpoint / handler — no "trust the caller" | CRITICAL |
| Input validated at the boundary — size, type, format, character set, range | CRITICAL |
| No `target="_blank"` without `rel="noopener noreferrer"` — tabnabbing | CRITICAL |
| Weak crypto avoided — no MD5/SHA1 for security, no DES, no ECB mode, no fixed IV | CRITICAL |
| Random for security uses CSPRNG — no `Math.random` / `Random` for tokens / IDs | CRITICAL |
| No logged PII / secrets / full tokens — sensitive data filtered before logging | WARNING |

### 1.3 Null Safety

Null mistakes are the single biggest source of runtime crashes. Apply this section to every nullable value (props, API responses, query params, DB rows, env vars, `find`/`first`-style returns, optional fields).

| Check | Severity if violated |
|---|---|
| Unguarded property access on a value that can be null/undefined/None (e.g., `user.profile.name` where `user` may be null) | CRITICAL |
| Non-null assertion / force-unwrap on a value sourced from props, API, env, or `URLSearchParams.get` (`!` in TS/Kotlin, `!!` in Kotlin/Dart, `.unwrap()` in Rust patterns) | CRITICAL |
| `JSON.parse` / equivalent without try/catch around untrusted input | CRITICAL |
| `find` / `first` / `at` result used without a presence check | WARNING |
| Default for a nullable parameter missing where the consumer assumes a value | WARNING |
| Optional chaining used on a value the type system already guarantees — defensive over-coding | INFO |
| Mixed conventions — some funcs use `null`, others `undefined`, others empty string for "missing" | WARNING |
| `Object.entries` / `Object.keys` on a value that may be null | WARNING |
| Dereferencing an array element by index without length check (`arr[0].x` on possibly empty array) | WARNING |
| Map / dict lookup result used without a presence check | WARNING |

### 1.4 Type Safety / Type Cast

| Check | Severity if violated |
|---|---|
| No `any` / `dynamic` / raw `object` / `interface{}` in public API surface | CRITICAL |
| No suppression of the type checker (`@ts-ignore`, `@ts-nocheck`, `# type: ignore`, `@SuppressWarnings("unchecked")`, `#pragma warning disable`) without an inline justification | CRITICAL |
| No unsafe cast — `as Foo`, `(Foo)x`, `cast<T>`, `Foo.cast(x)` — without a runtime check that proves the shape | CRITICAL |
| No double-cast laundering (`as unknown as Foo`, `(object)(Foo)x`) — that's a type system override | CRITICAL |
| Public functions / methods have explicit return types | WARNING |
| Generic types used where appropriate (don't lose type info via `object` / `any[]`) | WARNING |
| Type narrowing (type guards, pattern match) preferred over assertions | WARNING |
| Type definitions match runtime shape (no "lies" — types say `string`, runtime is `string \| null`) | CRITICAL |
| No mixing of nominal-vs-structural assumptions (e.g., `as` between unrelated branded types) | CRITICAL |
| Numeric types appropriate — no implicit narrowing (`number` for things that should be `bigint`, `int` for things that need `long`) | WARNING |

### 1.5 OOP Design

Apply when the code uses classes, interfaces, inheritance, or any other OO construct.

| Check | Severity if violated |
|---|---|
| **SRP** — class does one thing. Red flag: > 10 public methods spanning unrelated concerns; class name contains "Manager"/"Helper"/"Utils"/"Handler" while doing 3+ jobs | WARNING |
| **OCP** — adding a new variant doesn't require editing every existing branch. Red flag: `switch` on `type` field repeated across many call sites | WARNING |
| **LSP** — subtype is substitutable. Red flag: subtype throws "not supported", subtype overrides to no-op, subtype changes return type contract | CRITICAL |
| **ISP** — clients depend only on what they use. Red flag: interface with 15 methods where most callers implement 2 | WARNING |
| **DIP** — depends on abstractions. Red flag: class news up its own dependencies (`new SqlConnection(...)`) instead of receiving them | WARNING |
| Composition over inheritance — no deep inheritance chains (> 2 levels) just to share code | WARNING |
| No god-class — file with > ~500 lines, > 10 public methods, mixing many responsibilities | WARNING |
| No anemic-then-procedural pattern — data class + service class manipulating it from outside (move behavior next to data when sensible) | INFO |
| Encapsulation — fields not exposed unless intentional; getters/setters don't simply re-expose mutable internals | WARNING |
| Immutability where appropriate — value types are immutable; collections returned as read-only views | WARNING |
| `equals` / `hashCode` / `==` / `__eq__` consistent — never one without the other; equal objects have equal hashes | CRITICAL |
| No static mutable singletons holding business state — testability and lifecycle nightmares | CRITICAL |
| No friend-class workarounds — exposing internals "just for tests" or "just for one caller" | WARNING |
| Inheritance reflects "is-a", not "has-a" or "code reuse" | WARNING |

### 1.6 Design Patterns (suggest)

These are suggestions, not violations. Emit as **INFO** with category `Design Patterns (suggest)` unless the misuse causes a real bug — then escalate.

| Smell → suggested pattern | When to suggest |
|---|---|
| `switch`/`if-else` on a `kind`/`type` field repeated in many places → **Strategy** or **polymorphic dispatch** | The same switch shape appears ≥ 3 times across the codebase |
| Building a complex object via many `setX` calls in a fixed order → **Builder** | Constructor takes > 4 args OR object isn't valid until many setters are called |
| Wrapping a third-party API to fit our shape → **Adapter** | Cross-boundary type mismatch repeated at each call site |
| Notifying many listeners of an event → **Observer** / event bus | `for (x of subscribers) x.notify(...)` open-coded everywhere |
| Choosing implementation at runtime from config → **Factory** | `if (cfg.kind == 'A') new A() else new B()` in many places |
| Wrapping data access behind a uniform interface → **Repository** | Raw SQL / HTTP / ORM scattered across business logic |
| Adding cross-cutting behavior (logging, retry, caching) → **Decorator** / middleware | Boilerplate wrapping at every call site |
| Defining an algorithm skeleton with replaceable steps → **Template Method** / hook | Inheritance used purely to inject 1-2 methods |
| Returning `null` to mean "missing" everywhere → **Null Object** / Option type | Caller code is dominated by null checks |
| Lots of two-way conversions between A and B → **Mapper** | Inline mapping logic duplicated |
| **Misapplied** Singleton — used as a global for mutable state → recommend dependency injection | Singleton holds non-config state |
| **Misapplied** Visitor — applied to a tree that changes shape frequently → recommend polymorphism | Each new node type breaks every visitor |
| **Misapplied** Inheritance — used for code reuse, not "is-a" → recommend composition | Subclass and superclass don't share an interface contract |
| **Misapplied** Observer — listeners hold strong refs and leak memory → recommend weak refs / unsubscribe contract | Subscribe with no unsubscribe |

### 1.7 Error Handling

| Check | Severity if violated |
|---|---|
| No bare `catch` — catch specific types only | WARNING |
| No swallowed exception — logged or re-thrown; never `catch { }` | CRITICAL |
| No raw stack trace surfaced to the user — wrap with a user-friendly message; log the trace | WARNING |
| Retry only for transient failures, with backoff and a cap; never blind retry | WARNING |
| Cleanup in `finally` / `using` / `with` / `defer` — releases resources even on exception | CRITICAL |
| Errors carry actionable context — message says what failed and how to recover | WARNING |
| No "exception as control flow" for non-exceptional cases (returning via throw inside hot paths) | WARNING |
| Async errors propagate — every awaitable is awaited or its rejection is explicitly handled | CRITICAL |
| Don't catch-and-rethrow with no transformation — wastes a stack frame, loses cause chain | INFO |

### 1.8 Performance

| Check | Severity if violated |
|---|---|
| No unnecessary work in hot paths — sorting / parsing / regex compile / formatter creation on every call | WARNING |
| No N+1 — batch DB / HTTP / file calls when iterating | WARNING |
| Pagination present for endpoints / queries that can return unbounded rows | WARNING |
| No sync I/O on an async / event loop — `readFileSync`, `Task.Result`, `.Wait()`, blocking `requests` call inside `asyncio` | CRITICAL |
| Caching where the input domain is small and computation is expensive | INFO |
| No memory leaks — subscriptions, timers, listeners unsubscribed; large buffers released | CRITICAL |
| No allocations in tight loops — pre-size collections, reuse buffers where applicable | WARNING |
| Right data structure — `Set`/`HashMap` for lookup, not linear scan in a loop | WARNING |
| Regex / formatter / `Intl.NumberFormat` / `DateTimeFormatter` constructed once, not per-call | WARNING |
| Lazy loading where appropriate — don't load 10 MB upfront for a "maybe needed" view | INFO |
| String building uses a builder / join in hot loops — not `+=` on long strings | WARNING |
| Boxing avoided in hot numeric loops (Java, C#) | INFO |
| No O(n²) where O(n log n) or O(n) is reachable | WARNING |

### 1.9 Duplicate / DRY

| Check | Severity if violated |
|---|---|
| No copy-paste block ≥ ~6 lines duplicated between files | WARNING |
| No short block (≥ ~3 lines) duplicated ≥ 3 times in the codebase | WARNING |
| No duplicate constants — same magic value defined in multiple files | WARNING |
| No duplicate type definitions — same shape declared as two unrelated types | WARNING |
| No parallel hierarchies — `User` / `UserDto` / `UserView` / `UserModel` with the same fields, no shared source of truth | WARNING |
| No "shotgun surgery" — same change must be applied in N places for one logical edit | WARNING |
| When two callers diverge slightly, extract the common core + parameterize the diff; don't fork | INFO |

When suggesting a fix for a duplicate, point to **both** locations and propose where the shared helper should live (e.g., `src/shared/dateRange.ts`).

### 1.10 Unused / Dead Code

| Check | Severity if violated |
|---|---|
| Unused imports | WARNING |
| Unused locals / parameters (allow `_` / `unused` naming convention where the language requires the param) | WARNING |
| Unused private functions / methods | WARNING |
| Unreachable code — branches after `return` / `throw` / `break` | CRITICAL |
| Dead feature flag — flag is hardcoded `true` / `false` for > 1 release | WARNING |
| Commented-out code — delete it; git remembers | WARNING |
| Unused exports from a module (where the language has tooling to detect — `ts-prune`, `unimport`, etc.) | INFO |
| TODO without an owner / ticket — `// TODO:` with no `// TODO(@user/#123):` | WARNING |
| `console.log` / `print` / debug statements left in production code | WARNING |

### 1.11 Over-engineering

Apply these when the code does **more** than its current requirements need.

| Check | Severity if violated |
|---|---|
| Interface with one implementation and one caller — inline it; reintroduce when a second impl appears | WARNING |
| Abstract base class with one concrete subclass | WARNING |
| Generic / parameterized type that's never instantiated with more than one concrete | INFO |
| Configurable option that no caller ever changes from default | INFO |
| Factory-of-factories / builder-of-builders for a value that has one canonical construction | WARNING |
| Deep inheritance (> 2 levels) for a leaf type | WARNING |
| Plugin / extension point with no second plugin | INFO |
| "Just in case" hooks, callbacks, or event listeners no one subscribes to | WARNING |
| Premature performance optimization — micro-bench-driven complexity in non-hot code | WARNING |
| Speculative DSL / mini-language to avoid 10 lines of straightforward code | WARNING |

### 1.12 Under-engineering

Apply when the code does **less** than its current requirements demand.

| Check | Severity if violated |
|---|---|
| Magic numbers / strings — `if (x > 86400)`, `if (status == "active")` without named constant | WARNING |
| No validation at trust boundary — request handler / API endpoint trusts caller-supplied shape | CRITICAL |
| Copy-paste instead of a helper — see Duplicate / DRY section | WARNING |
| No abstraction at obvious boundary — raw SQL in a controller, raw HTTP in a domain class, raw file IO in a hot loop | WARNING |
| Hard-coded environment values — URLs, ports, credentials embedded in code instead of config | CRITICAL |
| Hard-coded user-facing strings without i18n in a project that requires localization | WARNING |
| No types where the language supports them — `any` / `dict` / `Map<string, object>` smuggled through public API | CRITICAL |
| No error type — every failure is a generic `Error` / `Exception` | WARNING |
| Public function with no docstring / JSDoc in a project whose standard requires it | INFO |
| No tests on a non-trivial branch in code marked for production | WARNING |

### 1.13 Standards

| Check | Severity if violated |
|---|---|
| Naming follows the project / language convention (see project rules) | WARNING |
| One concept per file — no `utils.ts` dumping ground | WARNING |
| Imports organized (per language / project convention) | INFO |
| No `TODO` without owner / ticket reference | WARNING |
| No debug logs / `print` / `console.log` left in production code | WARNING |
| Public functions named for what they do, not how (`fetchUser` not `httpGetUserById`) | INFO |
| Booleans named affirmatively (`isReady` not `notReady`) | INFO |
| File header comments don't exist (license headers excepted — those follow project policy) | INFO |

---

## Part 2 — Stack-specific overlays

After the universal pass, run the matching table(s) for the detected stack(s).

### 2.1 TypeScript / JavaScript

| Check | Severity if violated |
|---|---|
| `any` in source — use `unknown` + narrowing | CRITICAL |
| `@ts-ignore` / `@ts-nocheck` / `@ts-expect-error` without justification | CRITICAL |
| `as` cast without a preceding narrow — laundering | CRITICAL |
| `JSON.parse` without try/catch on untrusted input | CRITICAL |
| `Object.assign({}, target)` where spread `{...target}` is clearer | INFO |
| `==` / `!=` instead of `===` / `!==` | WARNING |
| Top-level await in a non-module / non-ESM context | CRITICAL |
| `Promise` created but never awaited / returned | CRITICAL |
| Unhandled promise rejection — async fn invoked without await/then-catch | CRITICAL |
| `void` used to discard a promise — only OK with comment explaining why | WARNING |
| Mutating an exported / frozen object | CRITICAL |
| `for...in` on an array (use `for...of` / indices) | WARNING |
| Optional chaining on a value the type already guarantees | INFO |
| Enum used where a union of string literals would be safer | INFO |
| Date constructed with implicit timezone assumption | WARNING |

### 2.2 C# / .NET

| Check | Severity if violated |
|---|---|
| `.Result` / `.Wait()` on a `Task` — risks deadlock on captured sync contexts | CRITICAL |
| `async void` outside of event handlers — exceptions crash the process | CRITICAL |
| `dynamic` in business code — defeats compile-time checking | CRITICAL |
| `catch (Exception) { }` — bare swallow | CRITICAL |
| Missing `ConfigureAwait(false)` in library code (per project policy) | WARNING |
| `IDisposable` not disposed — missing `using` / `await using` | CRITICAL |
| `Task.Run` for CPU-bound work inside an already-async handler | WARNING |
| Boxing in a hot loop (struct boxed to `object` / interface) | WARNING |
| `string` concatenation in a loop instead of `StringBuilder` | WARNING |
| LINQ `Count() > 0` instead of `Any()` on `IEnumerable` | WARNING |
| `IEnumerable<T>` enumerated multiple times — materialize once with `ToList()` | WARNING |
| Public mutable fields — use properties | WARNING |
| `Equals` / `GetHashCode` inconsistent — override both or neither | CRITICAL |
| `#pragma warning disable` without justification | WARNING |
| Nullable-reference warnings suppressed instead of fixed (`!`) | CRITICAL |

### 2.3 Python

| Check | Severity if violated |
|---|---|
| Mutable default argument (`def f(x=[])` / `def f(x={})`) — shared across calls | CRITICAL |
| `except:` / `except Exception: pass` — silent swallow | CRITICAL |
| `eval` / `exec` of untrusted input | CRITICAL |
| `pickle.loads` of untrusted input | CRITICAL |
| `subprocess.*(..., shell=True)` with interpolated user input | CRITICAL |
| `os.system` with interpolated input | CRITICAL |
| `# type: ignore` / `# noqa` without justification | WARNING |
| Type hints missing on public functions (per project policy) | WARNING |
| `requests` (sync) inside `asyncio` code — blocks the loop | CRITICAL |
| Bare `assert` for runtime input validation — assertions are stripped with `-O` | CRITICAL |
| `is` used for value equality on non-singleton objects (use `==`) | CRITICAL |
| `from X import *` in non-stub modules | WARNING |
| Module-level side effects (DB connect, file IO) at import time | WARNING |
| Iterating a dict while mutating it | CRITICAL |
| `open()` without context manager (`with`) | WARNING |
| `print` left in production code | WARNING |

### 2.4 Java / Kotlin

| Check | Severity if violated |
|---|---|
| Raw types (`List` instead of `List<T>`) | WARNING |
| `@SuppressWarnings("unchecked")` without justification | WARNING |
| `catch (Exception e)` catch-all | WARNING |
| `printStackTrace()` in production code | WARNING |
| `Thread.sleep` in business code | WARNING |
| Public mutable static field | CRITICAL |
| `equals` / `hashCode` inconsistent | CRITICAL |
| `Optional` used for fields / parameters (it's a return-type tool) | WARNING |
| **Kotlin:** `!!` force-unwrap on a value sourced from outside | CRITICAL |
| **Kotlin:** `lateinit var` on a non-DI field | WARNING |
| **Kotlin:** `runBlocking` inside a suspending context | CRITICAL |
| `ExecutorService` not shut down | CRITICAL |
| Resources (`InputStream`, `Connection`) not closed via try-with-resources / `use` | CRITICAL |

### 2.5 Go

| Check | Severity if violated |
|---|---|
| `panic` in library code for recoverable conditions | CRITICAL |
| Ignored error (`_ = doThing()`) without justification | WARNING |
| `interface{}` / `any` in public API where a concrete type would do | WARNING |
| Goroutine leak — goroutine spawned with no termination path | CRITICAL |
| Mutex copied (passed by value) | CRITICAL |
| Map access without comma-ok where presence matters | WARNING |
| `time.Sleep` for synchronization in business code | WARNING |
| Errors compared with `==` to wrapped values — use `errors.Is` / `errors.As` | WARNING |
| `fmt.Println` / `log.Println` instead of project's structured logger | WARNING |
| Slice of `defer`s in a loop that runs many times | WARNING |
| Returning a pointer to a stack-local that's then mutated (escape analysis surprises) | WARNING |
| Context not propagated through call chain | WARNING |
| Channel send without close strategy → leak | CRITICAL |

### 2.6 Dart / Flutter

| Check | Severity if violated |
|---|---|
| `dynamic` in public API | CRITICAL |
| `!` (force-unwrap) on a value sourced from outside | CRITICAL |
| `as` cast without a runtime check | WARNING |
| `print` left in production code | WARNING |
| `// ignore:` / `// ignore_for_file:` without justification | WARNING |
| `setState` called after `dispose` — guard with `mounted` | CRITICAL |
| `async` work scheduled from `build` | CRITICAL |
| `FutureBuilder` / `StreamBuilder` snapshot used without `hasData` / `hasError` checks | WARNING |
| Listeners / streams subscribed without cancellation in `dispose` | CRITICAL |
| `Navigator` / `BuildContext` used across an `await` without `mounted` check | CRITICAL |
| Long-lived `Timer` not cancelled | CRITICAL |
| Hard-coded colors / sizes — use Theme / tokens | WARNING |
| Widget rebuilds an expensive subtree on every frame (consider `const` / `RepaintBoundary`) | INFO |

### 2.7 SQL

| Check | Severity if violated |
|---|---|
| `SELECT *` in production queries | WARNING |
| String-built query with user input — injection | CRITICAL |
| `DELETE` / `UPDATE` without `WHERE` | CRITICAL |
| `NOLOCK` / `READ UNCOMMITTED` in OLTP without explicit reason | CRITICAL |
| Implicit type conversion in `WHERE` (e.g., `varchar = int`) — kills index | WARNING |
| `LIKE '%foo%'` on a large table without a full-text index | WARNING |
| Cursor / row-by-row loop where a set-based query would work | WARNING |
| Missing index hinted by query plan (`Seq Scan` on a large table in a hot query) | WARNING |
| `OR` in `WHERE` that defeats an index — consider `UNION ALL` or rewriting | INFO |
| Schema-modifying DDL inside a transaction that also moves data — lock duration risk | WARNING |
| No `LIMIT` / `TOP` on user-facing queries that could return unbounded rows | WARNING |
| Triggers used for cross-row business logic that belongs in app code | WARNING |

### 2.8 CSS / SCSS

| Check | Severity if violated |
|---|---|
| Hardcoded color / size — use design tokens (`var(--*)`) | CRITICAL |
| `!important` without a documented justification | WARNING |
| `$variable` SCSS vars in a project standardized on `var(--*)` | CRITICAL |
| `@mixin` / `@include` / `@function` in a project standardized on plain CSS + BEM | CRITICAL |
| Non-existent token namespace (`--bd-*`, `--bnds-*`, `--bnds-g-*`) | CRITICAL |
| Physical direction property (`margin-left`, `padding-right`, `left: 0`) where a logical property is required | WARNING |
| Selector specificity > 3 levels of nesting | WARNING |
| Inline `style="..."` in HTML / templates | CRITICAL |
| Class names not following project's naming convention (e.g., BEM) | INFO |
| Vendor prefixes that the project's autoprefixer / build pipeline already handles | INFO |

---

## Part 3 — Category vocabulary (use these exact labels in the report)

Pick one per finding. If a finding fits two categories, pick the more specific one; if it fits `Security` and another, pick `Security`.

| Category label | Used for |
|---|---|
| `Correctness` | Logic errors, off-by-one, wrong operators, race conditions, edge cases, ignored returns |
| `Security` | Injection (SQL/XSS/cmd/path), secrets in source, weak crypto, broken auth, unsafe deserialization |
| `Null Safety` | Unguarded access on nullable, non-null assertion on untrusted, missing default, defensive over-coding |
| `Type Safety / Type Cast` | `any`/`dynamic`, unsafe casts, type-checker suppression, lying types |
| `OOP Design` | SOLID violations, god-class, deep inheritance, exposed internals, mutable shared state |
| `Design Patterns (suggest)` | Where a known pattern would simplify; misapplied patterns |
| `Error Handling` | Bare catch, swallowed exceptions, raw stack traces, missing cleanup |
| `Performance` | Hot-path work, N+1, sync I/O in async, missing pagination/caching, re-created formatters |
| `Duplicate / DRY` | Copy-paste blocks, duplicate constants/types, parallel hierarchies |
| `Unused / Dead` | Unused imports/params/locals/functions, unreachable code, dead flags, commented-out code |
| `Over-engineering` | Premature abstraction, speculative generics, factory-of-factories, unused configurability |
| `Under-engineering` | Magic numbers, missing validation at boundary, copy-paste, hard-coded env values |
| `Standards` | Naming, file org, import order, debug logs, TODO without ticket |
| `Stack-specific` | Anything from Part 2 that doesn't cleanly fit the categories above (use sparingly — prefer a Part 1 label) |

---

## Part 4 — Report template

The reviewer writes this to `summary.vins.md` (or `--out`):

```markdown
# Code Review — <target>

- **Reviewed:** <ISO date>
- **Reviewer:** bnac-reviewer
- **Target:** <path>
- **Files reviewed:** <N>
- **Detected stack(s):** <e.g., TypeScript (primary), SCSS>
- **Output path:** <resolved path>

## Findings

| # | Severity | File:Line | Category | Issue | Suggested Fix |
|---|----------|-----------|----------|-------|---------------|
| 1 | CRITICAL | src/auth/login.ts:42 | Security | SQL string concat of `username` | Parameterize via prepared statement |
| 2 | CRITICAL | src/auth/login.ts:58 | Null Safety | `user.profile.name` — `user` is `User \| null` | Guard with `user?.profile?.name` or early return |
| 3 | WARNING  | src/auth/login.ts:71 | Type Safety / Type Cast | `as any` to silence error | Narrow with type guard or `unknown` + check |
| 4 | WARNING  | src/auth/utils.ts:15 | Under-engineering | Magic number `86400` | Extract to `SECONDS_PER_DAY` |
| 5 | WARNING  | src/auth/utils.ts:30-60 | Duplicate / DRY | 22 lines duplicated from `src/billing/utils.ts:80-100` | Extract to `src/shared/dateRange.ts` |
| 6 | WARNING  | src/auth/Provider.ts:1 | OOP Design | God-class: 14 public methods spanning auth + billing + telemetry | Split per SRP |
| 7 | INFO     | src/auth/Strategy.ts | Design Patterns (suggest) | Three `if/else` chains on `kind` field | Apply Strategy pattern |
| 8 | WARNING  | src/auth/login.ts:120 | Unused / Dead | Function `legacyValidate` not referenced | Delete or wire up |
| 9 | WARNING  | src/auth/Factory.ts | Over-engineering | Interface `IUserFactory` has one impl, one caller | Inline; reintroduce when 2nd impl appears |
| 10| WARNING  | src/auth/Login.tsx:10 | Performance | Inline `{}` passed to memoised child | Hoist via `useMemo` |

## Summary

- **CRITICAL:** 2
- **WARNING:** 6
- **INFO:** 2
- **Total:** 10
- **Verdict:** REQUEST CHANGES

## By category

| Category | CRITICAL | WARNING | INFO |
|----------|----------|---------|------|
| Security | 1 | 0 | 0 |
| Null Safety | 1 | 0 | 0 |
| Type Safety / Type Cast | 0 | 1 | 0 |
| Under-engineering | 0 | 1 | 0 |
| Duplicate / DRY | 0 | 1 | 0 |
| OOP Design | 0 | 1 | 0 |
| Design Patterns (suggest) | 0 | 0 | 1 |
| Unused / Dead | 0 | 1 | 0 |
| Over-engineering | 0 | 1 | 0 |
| Performance | 0 | 1 | 0 |

## Notes

Detected stack was TypeScript (primary) with SCSS. If this folder also contains Go files, re-run scoped to the Go folder so the Go overlay applies.
```
