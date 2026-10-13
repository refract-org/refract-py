# refract-py

> **This repository has moved.** The adapter is now
> [`clients/python`](https://github.com/refract-org/refract/tree/main/clients/python) in
> [refract-org/refract](https://github.com/refract-org/refract), imported with
> its full history. Install it from there:
>
> ```bash
> pip install "git+https://github.com/refract-org/refract.git#subdirectory=clients/python"
> ```
>
> That version also ships `refract_eval` and `refract_langchain`, which the wheel
> built from this repository leaves out. The install below still works, but it
> stays at this repository's last commit. Open issues and pull requests in
> refract-org/refract; this repository is kept read-only for its history.

Python SDK for [Refract](https://github.com/refract-org/refract) — the open claim-history layer for public knowledge.

```bash
pip install git+https://github.com/refract-org/refract-py.git  # not on PyPI yet
```

Requires the [Refract CLI](https://github.com/refract-org/refract):
```bash
npm install -g @refract-org/cli
```

## Usage

```python
from refract import Refract

r = Refract()

# Analyze a page, get typed dataclasses
events = r.analyze("Bitcoin", depth="brief")
for event in events:
    print(event.eventType, event.timestamp)

# Export as pandas DataFrame
df = r.analyze("Bitcoin", depth="forensic", as_frame=True)
print(df.groupby("event_type").size())

# Export flattened CSV-compatible rows
df = r.export("Bitcoin", format="ndjson", flatten=True, as_frame=True)
```

## Integrations

| Tool | How |
|---|---|
| **pandas** | `as_frame=True` returns DataFrames with flattened provenance fields |
| **Jupyter** | Analyze pages, plot citation churn, export findings — all from a notebook |
| **LangChain** | `refract_langchain.py` loads events as `Document` objects with stability metadata for provenance-aware RAG |
| **DuckDB** | Export as NDJSON, query with SQL: `SELECT * FROM 'events.jsonl'` |

See the [Python SDK tutorial](https://refract-org.github.io/refract-docs/tutorials/python-sdk/) and [integrations docs](https://refract-org.github.io/refract-docs/integrations/) for full workflows.

## License

AGPL-3.0.
