from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

BRONZE_PATH = PROJECT_ROOT / "data" / "raw" / "csv"
SILVER_PATH = PROJECT_ROOT / "data" / "silver"

datasets = ["customers", "orders", "products"]

total_bronze = 0
total_silver = 0

print("=" * 70)
print("BRONZE CSV VS SILVER PARQUET STORAGE COMPARISON")
print("=" * 70)

for dataset in datasets:

    csv_file = BRONZE_PATH / f"{dataset}.csv"
    parquet_file = SILVER_PATH / dataset / f"{dataset}.parquet"

    bronze_size = csv_file.stat().st_size
    silver_size = parquet_file.stat().st_size

    total_bronze += bronze_size
    total_silver += silver_size

    reduction = (
        (bronze_size - silver_size) / bronze_size * 100
        if bronze_size > 0
        else 0
    )

    print(f"\nDataset: {dataset}")
    print("-" * 50)
    print(f"Bronze CSV:   {bronze_size / 1024:.2f} KB")
    print(f"Silver Parquet: {silver_size / 1024:.2f} KB")
    print(f"Size reduction: {reduction:.2f}%")

print("\n" + "=" * 70)
print("TOTAL COMPARISON")
print("=" * 70)

total_reduction = (
    (total_bronze - total_silver) / total_bronze * 100
    if total_bronze > 0
    else 0
)

print(f"Total Bronze: {total_bronze / 1024:.2f} KB")
print(f"Total Silver: {total_silver / 1024:.2f} KB")
print(f"Total reduction: {total_reduction:.2f}%")
print("=" * 70)