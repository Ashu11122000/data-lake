
import json
from pathlib import Path

import pandas as pd
from PIL import Image

# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# =========================================================
# CSV INSPECTION
# =========================================================

def inspect_csv_files():
    print("\n" + "=" * 70)
    print("CSV DATASET INSPECTION")
    print("=" * 70)

    csv_dir = RAW_DIR / "csv"

    for file_path in csv_dir.glob("*.csv"):
        print(f"\nFILE: {file_path.name}")

        df = pd.read_csv(file_path)

        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")

        print("\nSchema:")
        for column, dtype in df.dtypes.items():
            print(f"  {column}: {dtype}")

        print("\nSample records:")
        print(df.head(3).to_string(index=False))

# =========================================================
# JSON INSPECTION
# =========================================================

def inspect_json_files():
    print("\n" + "=" * 70)
    print("JSON DATASET INSPECTION")
    print("=" * 70)

    json_dir = RAW_DIR / "json"

    for file_path in json_dir.glob("*.json"):
        print(f"\nFILE: {file_path.name}")

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            print(f"Top-level structure: List")
            print(f"Record count: {len(data)}")

            if data:
                print("\nFields in first record:")

                for key, value in data[0].items():
                    print(f"  {key}: {type(value).__name__}")

                    if isinstance(value, dict):
                        print("    Nested fields:")

                        for nested_key, nested_value in value.items():
                            print(
                                f"      {nested_key}: "
                                f"{type(nested_value).__name__}"
                            )

                print("\nFirst record:")
                print(json.dumps(data[0], indent=4))

        elif isinstance(data, dict):
            print("Top-level structure: Dictionary")

            print("\nTop-level fields:")

            for key, value in data.items():
                if isinstance(value, list):
                    print(f"  {key}: list ({len(value)} records)")

                    if value:
                        print("    First item structure:")

                        for nested_key, nested_value in value[0].items():
                            print(
                                f"      {nested_key}: "
                                f"{type(nested_value).__name__}"
                            )

                elif isinstance(value, dict):
                    print(f"  {key}: dictionary")

                else:
                    print(f"  {key}: {type(value).__name__}")

# =========================================================
# LOG INSPECTION
# =========================================================

def inspect_log_files():
    print("\n" + "=" * 70)
    print("LOG FILE INSPECTION")
    print("=" * 70)

    log_dir = RAW_DIR / "logs"

    for file_path in log_dir.glob("*.log"):
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        print(f"\nFILE: {file_path.name}")
        print(f"Total log lines: {len(lines)}")

        print("\nFirst 5 log entries:")

        for line in lines[:5]:
            print(line.rstrip())

# =========================================================
# TEXT FILE INSPECTION
# =========================================================

def inspect_text_files():
    print("\n" + "=" * 70)
    print("TEXT FILE INSPECTION")
    print("=" * 70)

    text_dir = RAW_DIR / "text"

    for file_path in text_dir.glob("*.txt"):
        content = file_path.read_text(encoding="utf-8")

        print(f"\nFILE: {file_path.name}")
        print(f"Characters: {len(content)}")
        print(f"File size: {file_path.stat().st_size} bytes")

        print("\nSample content:")
        print(content[:300])

# =========================================================
# IMAGE INSPECTION
# =========================================================

def inspect_image_files():
    print("\n" + "=" * 70)
    print("IMAGE INSPECTION")
    print("=" * 70)

    image_dir = RAW_DIR / "images"

    for file_path in image_dir.iterdir():
        if not file_path.is_file():
            continue

        try:
            with Image.open(file_path) as image:
                print(f"\nFILE: {file_path.name}")
                print(f"Format: {image.format}")
                print(f"Dimensions: {image.width} x {image.height}")
                print(f"Mode: {image.mode}")
                print(f"File size: {file_path.stat().st_size} bytes")

        except Exception as error:
            print(f"Could not inspect {file_path.name}: {error}")

# =========================================================
# MAIN
# =========================================================

def main():
    print("=" * 70)
    print("RAW DATA INSPECTION REPORT")
    print("=" * 70)

    inspect_csv_files()
    inspect_json_files()
    inspect_log_files()
    inspect_text_files()
    inspect_image_files()

    print("\n" + "=" * 70)
    print("DATA INSPECTION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
