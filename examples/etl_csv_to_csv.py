"""Example: CSV -> transformed CSV using Universal ETL toolkit."""

from pathlib import Path
import csv

from universal_etl import ETLPipeline, dict_filter, dict_rename

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def extract_rows():
    src = DATA_DIR / "example_sales_raw.csv"
    with src.open(newline="", encoding="utf-8") as f:
        yield from csv.DictReader(f)


def load_rows(rows):
    dst = DATA_DIR / "example_sales_clean.csv"
    fieldnames = ["date", "product", "qty", "revenue"]
    with dst.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


pipeline = ETLPipeline(
    extract=extract_rows,
    transforms=[
        dict_filter(["date", "product", "quantity", "total_price"]),
        dict_rename({"quantity": "qty", "total_price": "revenue"}),
    ],
    load=load_rows,
    name="csv_clean_example",
)

if __name__ == "__main__":
    pipeline.run()
    print("Wrote cleaned file to", DATA_DIR / "example_sales_clean.csv")
