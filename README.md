# refract-py

Python SDK for [Refract](https://github.com/refract-org/refract) — the open claim-history layer for public knowledge.

```bash
pip install refract-py
```

Requires the [Refract CLI](https://github.com/refract-org/refract):
```bash
npm install -g @refract-org/cli
```

## Usage

```python
from refract import Refract

r = Refract()

# Analyze a page, get typed objects
events = r.analyze("Bitcoin", depth="brief")
for event in events:
    print(event.event_type, event.timestamp)

# Export as pandas DataFrame
df = r.analyze("Bitcoin", as_frame=True)
print(df.groupby("event_type").size())

# Export flattened CSV-compatible rows
df = r.export("Bitcoin", format="ndjson", flatten=True, as_frame=True)
```

## License

AGPL-3.0.
