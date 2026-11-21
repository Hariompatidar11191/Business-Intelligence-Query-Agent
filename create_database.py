
import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR / "sales_data_sample.csv"
DB_PATH = BASE_DIR / "sales.db"

if not CSV_PATH.exists():
    raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

# Read CSV with encoding fallback
for encoding in ["utf-8", "cp1252", "latin1"]:
    try:
        df = pd.read_csv(CSV_PATH, encoding=encoding)
        print(f"CSV loaded using {encoding}")
        break
    except UnicodeDecodeError:
        df = None

if df is None:
    raise ValueError("Unable to read CSV file.")

# Create SQLite database
with sqlite3.connect(DB_PATH) as conn:
    df.to_sql(
        "sales_data",
        conn,
        if_exists="replace",
        index=False
    )

print("Database created successfully!")
print("Total records:", len(df))
