# Agent Instructions for refract-py

Python SDK for [Refract](https://github.com/refract-org/refract) — wraps the Refract CLI via subprocess.

## Domain Boundary

This package wraps the `@refract-org/cli` JavaScript package. It does NOT add model logic, interpretation, or domain-specific judgment. It provides typed Python dataclasses and a convenience API over the CLI's JSON output.

## Build & Verify

```bash
hatch build    # Build wheel
hatch test     # Run pytest
```

## Conventions

- **Runtime**: Python 3.10+
- **Build**: Hatch
- **Test**: pytest
- **Types**: dataclasses from `src/refract/__init__.py` mirror `@refract-org/evidence-graph` schemas
- **CLI dependency**: Requires `refract` or `npx @refract-org/cli` on PATH
- **Error handling**: `RefractError` raised on non-zero CLI exit codes

## Forbidden

- Never add model calls, LLM inference, or ML logic to this SDK
- Never add healthcare-specific vocabulary (payer, clinical, guideline, etc.)
- Never add sentiment analysis, truth claims, or prediction
- The SDK observes — it does not interpret

## Commit Convention

Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`

## License

AGPL-3.0
