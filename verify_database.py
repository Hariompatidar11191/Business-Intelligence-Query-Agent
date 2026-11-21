
import sqlite3

conn = sqlite3.connect("sales.db")
cursor = conn.cursor()

# Check available tables
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
)
print("Tables:", cursor.fetchall())

# Check total records
cursor.execute("SELECT COUNT(*) FROM sales_data")
print("Total records:", cursor.fetchone()[0])

# Check column names
cursor.execute("PRAGMA table_info(sales_data)")
columns = cursor.fetchall()

print("Columns:")
for column in columns:
    print(column[1])

conn.close()
