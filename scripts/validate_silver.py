from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SILVER_PATH = PROJECT_ROOT / "data" / "silver"

datasets = [
    "customers",
    "orders",
    "products",
]

print("=" * 70)
print("SILVER LAYER VALIDATION")
print("=" * 70)

for dataset in datasets:

    file_path = (
        SILVER_PATH
        / dataset
        / f"{dataset}.parquet"
    )

    print(f"\nDataset: {dataset}")
    print("-" * 50)

    if not file_path.exists():
        print("ERROR: Parquet file does not exist!")
        continue

    # Read Parquet file
    df = pd.read_parquet(file_path)

    # File size
    file_size_bytes = file_path.stat().st_size
    file_size_kb = file_size_bytes / 1024

    # Display validation information
    print(f"File: {file_path.name}")
    print(f"Records: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"File size: {file_size_kb:.2f} KB")
    print(f"Null values: {df.isnull().sum().sum()}")
    print(f"Duplicate rows: {df.duplicated().sum()}")

    print("\nSchema:")
    print(df.dtypes)

    print("\nSample records:")
    print(df.head(3))

print("\n" + "=" * 70)
print("SILVER VALIDATION COMPLETED")
print("=" * 70)