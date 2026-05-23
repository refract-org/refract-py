# refract-py — Copilot Instructions

Python SDK for Refract. Wraps the Refract CLI via subprocess. Hatched builds.

## Quick Commands

```bash
pip install -e ".[dev]"   # Development install
hatch build                # Build wheel
hatch test                 # Run pytest
```

## Key Paths

- `src/refract/` — Python package source
- `tests/` — pytest test suite
- `pyproject.toml` — Project config

## Conventions

- **Runtime:** Python 3.10+
- **Build:** Hatch
- **Tests:** pytest
- **CI:** GitHub Actions (ci.yml)
- **Commit style:** Conventional Commits

## Important

- Never add model calls, LLM inference, or ML logic
- Never add healthcare-specific vocabulary
- The SDK observes — it does not interpret

## Pre-Commit Rule

```bash
hatch test   # Run before pushing.
```
