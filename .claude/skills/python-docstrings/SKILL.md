---
name: python-docstrings
description: Google-style and NumPy-style docstring conventions — when to use each, required sections, Sphinx integration notes, and docstring quality rules. Used by python-doc-writer.
user-invocable: false
argument-hint: ""
---

BusinessNext Python services use Google-style docstrings by default. NumPy-style is used in data-science or numerical computing modules where parameter tables are more readable. This skill defines the required sections for each style, when to write docstrings, and integration with Sphinx autodoc.

## Additional Resources

- [reference/google-style.md](reference/google-style.md) — complete Google-style docstring examples for functions, classes, and modules
- [reference/numpy-style.md](reference/numpy-style.md) — NumPy-style examples with section headers and parameter tables

## Steps

1. **Determine the style** — check `pyproject.toml` or project docs for the preferred style; default to Google
2. **Write the summary line** — one sentence, imperative mood (`Return the user.` not `Returns the user.`), no period not required but consistent within the project
3. **Write `Args:` / `Parameters`** — one entry per parameter; type is omitted if already in the annotation (do not duplicate)
4. **Write `Returns:` / `Returns`** — describe what is returned; omit if return type is `None`
5. **Write `Raises:` / `Raises`** — one entry per exception the function can raise; must cover all domain exceptions
6. **Write `Example:` / `Examples`** — for non-trivial public API; the example must be syntactically correct and representative
7. **Module docstring** — every `__init__.py` and every top-level module has a one-paragraph docstring describing its purpose

## Rules

- **Do not duplicate type annotations** — if the signature says `user_id: int`, the docstring says `user_id: Description.` not `user_id (int): Description.`
- **Raises section is mandatory when domain exceptions are raised** — undocumented exceptions break API consumers
- **Private functions get docstrings only if complex** — `_` prefixed helpers of > 10 lines should have a one-line summary at minimum
- **One docstring style per project** — never mix Google and NumPy in the same package
- **Examples must work** — the `Example:` block is not a comment; it should be runnable in isolation if possible
