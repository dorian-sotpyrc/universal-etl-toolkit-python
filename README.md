
# Universal ETL Toolkit in Python (Under 100 Lines)

A tiny, composable ETL core for Python that lets you:

- Read rows from any source (CSV, DB, API)
- Apply a small pipeline of pure functions (transform dicts → dicts)
- Write rows out to any sink (CSV, DB, API)

No frameworks, no orchestration engines — just a few functions you can drop into any project or notebook.

> This is the exact core used by the **PLEX ETL Playground** on [plexdata.online](https://plexdata.online).

---

## Why this exists

Most ETL tools jump straight to:

- YAML configs
- DAG schedulers
- 20 abstractions before you can move a single row

Sometimes you just want:

- “Read a CSV”
- “Keep these columns”
- “Rename a few things”
- “Write another CSV”

This repo is that: a **minimal ETL toolkit** that still feels like a real pattern you can embed in bigger systems.

---

## Features

- ✅ **Under 100 lines of core logic** (see `src/universal_etl.py`)
- ✅ **Composable pipeline** – chain any `dict -> dict | None` transforms  
- ✅ **Row-level control** – filter, rename, enrich, drop rows, etc.
- ✅ **Streaming-friendly** – generator-based, no huge in-memory dataframes required
- ✅ **Tested** – see `tests/test_universal_etl.py`
- ✅ **CSV example** – ready to run: `examples/etl_csv_to_csv.py`

Perfect for:

- Quick data cleanups
- Notebook prototypes that might grow up later
- Teaching ETL concepts without drowning in Airflow / dbt

---

## Installation

Clone and install in editable mode:

```bash
git clone https://github.com/dorian-sotpyrc/universal-etl-toolkit-python.git
cd universal-etl-toolkit-python

python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -e .
````

This exposes the module as:

```python
import universal_etl
```

---

## Quick start

The core concept is an `ETLPipeline` that:

* Takes an **extractor**: yields input rows as dictionaries
* Takes a **list of transforms**: functions `dict -> dict | None`
* Takes a **loader**: consumes transformed rows

### 1. Minimal example

```python
from universal_etl import ETLPipeline, dict_filter, dict_rename

def extract():
    # In real usage this might read from CSV, DB, API...
    rows = [
        {"order_id": "A1", "customer": "Alice", "total_price": 120.0},
        {"order_id": "B2", "customer": "Bob", "total_price": 15.0},
    ]
    for row in rows:
        yield row

def load(rows):
    for row in rows:
        print(row)

pipeline = ETLPipeline(
    extract=extract,
    transforms=[
        # Only keep “larger” orders
        dict_filter(lambda r: r.get("total_price", 0) >= 20),
        # Rename columns for downstream systems
        dict_rename({"order_id": "id", "total_price": "price"}),
    ],
    load=load,
)

pipeline.run()
```

Output:

```text
{'id': 'A1', 'customer': 'Alice', 'price': 120.0}
```

---

## Example: CSV → CSV

This repo ships with a runnable CSV example:

```bash
python examples/etl_csv_to_csv.py
```

It:

* Reads `data/example_sales_raw.csv`
* Filters / renames columns using the toolkit
* Writes a new file `example_sales_cleaned.csv` in the same folder

The script uses the same API you’d use in your own projects.

### Snippet from `examples/etl_csv_to_csv.py`

```python
from pathlib import Path
from universal_etl import ETLPipeline, dict_filter, dict_rename

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

input_path = DATA_DIR / "example_sales_raw.csv"
output_path = DATA_DIR / "example_sales_cleaned.csv"

def extract_csv(path):
    import csv
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

def load_csv(path, rows, fieldnames):
    import csv
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

pipeline = ETLPipeline(
    extract=lambda: extract_csv(input_path),
    transforms=[
        dict_filter(lambda r: r.get("quantity") not in (None, "", "0")),
        dict_rename({"order_id": "id", "total_price": "price"}),
    ],
    load=lambda rows: load_csv(
        output_path,
        rows,
        fieldnames=["id", "customer", "quantity", "price", "region", "channel"],
    ),
)

if __name__ == "__main__":
    pipeline.run()
    print(f"Wrote cleaned CSV to {output_path}")
```

---

## API reference (core building blocks)

All of this lives in `src/universal_etl.py`.

### `ETLPipeline`

```python
class ETLPipeline:
    def __init__(self, extract, transforms, load):
        ...
    def run(self):
        ...
```

* `extract`: `Callable[[], Iterable[dict]]`
* `transforms`: `list[Callable[[dict], dict | None]]`
* `load`: `Callable[[Iterable[dict]], None]`

Pipeline behaviour:

1. Calls `extract()` → gets rows (dicts)
2. Applies each transform in order

   * If a transform returns `None`, that row is **dropped**
   * Otherwise the returned dict is passed to the next transform
3. Passes the final row stream into `load(rows)`

---

### `dict_filter(predicate)`

Small helper to keep only rows matching a condition.

```python
from universal_etl import dict_filter

only_large_orders = dict_filter(lambda r: r.get("total_price", 0) >= 100)
```

* If `predicate(row)` is `True` → row continues
* If `False` → row is dropped (`None` returned)

---

### `dict_rename(mapping)`

Rename a subset of keys.

```python
from universal_etl import dict_rename

rename = dict_rename({"order_id": "id", "total_price": "price"})
```

* Keys not in `mapping` are left unchanged
* Only a shallow rename; values are passed through

---

## How this relates to PLEX

This toolkit powers the **PLEX ETL Playground** tool on [plexdata.online](https://plexdata.online):

* The browser tool handles:

  * CSV upload
  * Column selection (keep/drop)
  * Rename rules (`old=new` style)
* The Flask backend uses this library to:

  * Parse the CSV header
  * Build a small `ETLPipeline`
  * Stream out a cleaned CSV back to the browser

The patterns in this repo are explained in the upcoming PLEX article:

> **“Build a Universal ETL Toolkit in Python in Under 100 Lines”**
> PLEX article: [https://plexdata.online/post/build-universal-etl-toolkit-python](https://plexdata.online/post/build-universal-etl-toolkit-python)

If you like the web version, you can:

* Clone this repo
* Copy the core (`ETLPipeline`, `dict_filter`, `dict_rename`) into your own project
* Point it at your own CSVs, APIs, or databases

---

## Design principles

* **Small, readable, copy-pastable**
  You should be able to open `universal_etl.py` and understand everything in a few minutes.

* **“Bring your own IO”**
  This toolkit doesn’t know about CSV, SQL, S3, or APIs. You wire those in via `extract` and `load`.

* **Composable, not magical**
  Transforms are just functions. You can write your own to:

  * Enrich rows from side tables
  * Normalise fields
  * Validate schema and drop bad rows

* **Upgrade path to bigger tools**
  Once your needs go beyond this, you can port the same extract / transform / load functions into
  Airflow, Dagster, Prefect, dbt, etc.

---

## Running tests

```bash
cd universal-etl-toolkit-python
pytest
```

The test suite covers:

* Basic pipeline behaviour
* Filtering
* Renaming

---

## Roadmap

Short-term ideas:

* Additional helpers:

  * `dict_project` (keep only selected keys)
  * `dict_const` (add constant fields)
  * `dict_map` (value-level mapping per key)
* Typed variants / mypy-friendly signatures
* A tiny “examples” directory for:

  * CSV → CSV
  * CSV → JSON Lines
  * ETL inside a Flask route (mirroring PLEX ETL Playground)

If you have suggestions, feel free to open an issue or PR.

---

## License



```text
Copyright (c) 2025 Dorian Sotpyrc
```

