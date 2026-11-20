"""
Bronze-to-Silver Data Cleaning Module

This module:
1. Reads raw Bronze CSV datasets.
2. Validates expected columns.
3. Handles missing values.
4. Removes duplicate records.
5. Standardizes data types.
6. Applies basic data quality rules.
7. Saves cleaned datasets in Parquet format to the Silver layer.
8. Generates processing statistics.
"""

from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "csv"
SILVER_DATA_PATH = PROJECT_ROOT / "data" / "silver"


# ============================================================
# DATASET CONFIGURATION
# ============================================================

DATASET_CONFIG = {
    "customers": {
        "source_file": "customers.csv",
        "expected_columns": [
            "customer_id",
            "customer_name",
            "email",
            "city",
            "region",
            "signup_date",
        ],
        "primary_key": "customer_id",
    },
    "orders": {
        "source_file": "orders.csv",
        "expected_columns": [
            "order_id",
            "customer_id",
            "order_date",
            "order_status",
            "payment_method",
        ],
        "primary_key": "order_id",
    },
    "products": {
        "source_file": "products.csv",
        "expected_columns": [
            "product_id",
            "product_name",
            "category",
            "price",
            "stock_quantity",
        ],
        "primary_key": "product_id",
    },
}


# ============================================================
# GENERIC DATA CLEANING FUNCTIONS
# ============================================================

def load_raw_csv(dataset_name: str) -> pd.DataFrame:
    """Load a Bronze CSV dataset."""

    config = DATASET_CONFIG[dataset_name]
    file_path = RAW_DATA_PATH / config["source_file"]

    if not file_path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {file_path}"
        )

    print(f"\nLoading dataset: {dataset_name}")
    print(f"Source: {file_path}")

    return pd.read_csv(file_path)


def validate_columns(
    df: pd.DataFrame,
    dataset_name: str
) -> None:
    """Validate that the dataset contains expected columns."""

    expected_columns = DATASET_CONFIG[dataset_name][
        "expected_columns"
    ]

    missing_columns = [
        column
        for column in expected_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{dataset_name} is missing required columns: "
            f"{missing_columns}"
        )

    print("Column validation: PASSED")


def remove_duplicates(
    df: pd.DataFrame,
    dataset_name: str
) -> pd.DataFrame:
    """Remove duplicate rows and duplicate primary keys."""

    original_count = len(df)

    df = df.drop_duplicates()

    primary_key = DATASET_CONFIG[dataset_name]["primary_key"]

    duplicate_keys = df[primary_key].duplicated().sum()

    if duplicate_keys > 0:
        print(
            f"Duplicate {primary_key} values found: "
            f"{duplicate_keys}"
        )

        df = df.drop_duplicates(
            subset=[primary_key],
            keep="first"
        )

    removed_count = original_count - len(df)

    print(f"Duplicate records removed: {removed_count}")

    return df


def standardize_column_names(
    df: pd.DataFrame
) -> pd.DataFrame:
    """Standardize column names."""

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df


# ============================================================
# CUSTOMER CLEANING
# ============================================================

def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the customers dataset."""

    print("\nCleaning customers dataset...")

    # Remove whitespace from string columns
    string_columns = [
        "customer_name",
        "email",
        "city",
        "region",
    ]

    for column in string_columns:
        df[column] = df[column].astype("string").str.strip()

    # Standardize email addresses
    df["email"] = df["email"].str.lower()

    # Convert signup date
    df["signup_date"] = pd.to_datetime(
        df["signup_date"],
        errors="coerce"
    )

    # Handle missing values
    df["customer_name"] = df["customer_name"].fillna(
        "Unknown Customer"
    )

    df["email"] = df["email"].fillna(
        "unknown@example.com"
    )

    df["city"] = df["city"].fillna(
        "Unknown"
    )

    df["region"] = df["region"].fillna(
        "Unknown"
    )

    # Remove records with invalid customer IDs
    df = df.dropna(subset=["customer_id"])

    # Convert customer ID to integer
    df["customer_id"] = pd.to_numeric(
        df["customer_id"],
        errors="coerce"
    )

    df = df.dropna(subset=["customer_id"])

    df["customer_id"] = df["customer_id"].astype("int64")

    # Remove duplicate customers
    df = df.drop_duplicates(
        subset=["customer_id"],
        keep="first"
    )

    # Keep records with valid dates
    df = df.dropna(subset=["signup_date"])

    print("Customer cleaning completed")

    return df


# ============================================================
# ORDER CLEANING
# ============================================================

def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the orders dataset."""

    print("\nCleaning orders dataset...")

    # Standardize text fields
    string_columns = [
        "order_status",
        "payment_method",
    ]

    for column in string_columns:
        df[column] = df[column].astype("string").str.strip()

    # Standardize order status capitalization
    df["order_status"] = df["order_status"].str.title()

    # Standardize payment method capitalization
    df["payment_method"] = df["payment_method"].str.title()

    # Convert order date
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )

    # Convert identifiers
    df["order_id"] = pd.to_numeric(
        df["order_id"],
        errors="coerce"
    )

    df["customer_id"] = pd.to_numeric(
        df["customer_id"],
        errors="coerce"
    )

    # Remove invalid identifiers
    df = df.dropna(
        subset=["order_id", "customer_id"]
    )

    df["order_id"] = df["order_id"].astype("int64")
    df["customer_id"] = df["customer_id"].astype("int64")

    # Remove invalid order dates
    df = df.dropna(subset=["order_date"])

    # Remove duplicate orders
    df = df.drop_duplicates(
        subset=["order_id"],
        keep="first"
    )

    print("Order cleaning completed")

    return df


# ============================================================
# PRODUCT CLEANING
# ============================================================

def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the products dataset."""

    print("\nCleaning products dataset...")

    # Clean text fields
    string_columns = [
        "product_name",
        "category",
    ]

    for column in string_columns:
        df[column] = df[column].astype("string").str.strip()

    # Convert numeric fields
    df["product_id"] = pd.to_numeric(
        df["product_id"],
        errors="coerce"
    )

    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    df["stock_quantity"] = pd.to_numeric(
        df["stock_quantity"],
        errors="coerce"
    )

    # Remove records with invalid product IDs
    df = df.dropna(subset=["product_id"])

    df["product_id"] = df["product_id"].astype("int64")

    # Remove duplicate products
    df = df.drop_duplicates(
        subset=["product_id"],
        keep="first"
    )

    # Remove records with invalid prices
    df = df.dropna(subset=["price"])

    # Business rules
    df = df[df["price"] >= 0]

    # Invalid stock quantities are removed
    df = df.dropna(subset=["stock_quantity"])

    df["stock_quantity"] = df["stock_quantity"].astype("int64")

    # Missing descriptive fields
    df["product_name"] = df["product_name"].fillna(
        "Unknown Product"
    )

    df["category"] = df["category"].fillna(
        "Uncategorized"
    )

    print("Product cleaning completed")

    return df


# ============================================================
# DATA QUALITY REPORT
# ============================================================

def generate_report(
    dataset_name: str,
    original_df: pd.DataFrame,
    cleaned_df: pd.DataFrame
) -> dict:
    """Generate basic data quality and processing statistics."""

    report = {
        "dataset": dataset_name,
        "records_before": len(original_df),
        "records_after": len(cleaned_df),
        "records_removed": len(original_df) - len(cleaned_df),
        "columns": len(cleaned_df.columns),
        "null_values_after": int(
            cleaned_df.isnull().sum().sum()
        ),
        "duplicate_rows_after": int(
            cleaned_df.duplicated().sum()
        ),
    }

    return report


# ============================================================
# BRONZE TO SILVER PIPELINE
# ============================================================

def process_dataset(dataset_name: str) -> dict:
    """Process a single dataset from Bronze to Silver."""

    config = DATASET_CONFIG[dataset_name]

    # Load Bronze data
    raw_df = load_raw_csv(dataset_name)

    original_df = raw_df.copy()

    print(f"Original records: {len(raw_df)}")

    # Standardize column names
    raw_df = standardize_column_names(raw_df)

    # Validate schema
    validate_columns(raw_raw_df := raw_df, dataset_name=dataset_name)

    # Remove duplicate records
    raw_df = remove_duplicates(
        raw_df,
        dataset_name
    )

    # Apply dataset-specific cleaning
    if dataset_name == "customers":
        cleaned_df = clean_customers(raw_df)

    elif dataset_name == "orders":
        cleaned_df = clean_orders(raw_df)

    elif dataset_name == "products":
        cleaned_df = clean_products(raw_df)

    else:
        raise ValueError(
            f"Unsupported dataset: {dataset_name}"
        )

    # Create Silver directory
    output_directory = SILVER_DATA_PATH / dataset_name
    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save cleaned dataset as Parquet
    output_file = output_directory / f"{dataset_name}.parquet"

    cleaned_df.to_parquet(
        output_file,
        index=False,
        engine="pyarrow"
    )

    # Generate report
    report = generate_report(
        dataset_name,
        original_df,
        cleaned_df
    )

    print("\nProcessing Summary")
    print("----------------")
    print(f"Dataset: {dataset_name}")
    print(f"Records before: {report['records_before']}")
    print(f"Records after: {report['records_after']}")
    print(f"Records removed: {report['records_removed']}")
    print(f"Null values remaining: {report['null_values_after']}")
    print(f"Duplicate rows remaining: {report['duplicate_rows_after']}")
    print(f"Silver output: {output_file}")

    return report


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("BRONZE TO SILVER DATA PROCESSING")
    print("=" * 60)

    datasets_to_process = [
        "customers",
        "orders",
        "products",
    ]

    reports = []

    for dataset in datasets_to_process:
        report = process_dataset(dataset)
        reports.append(report)

    print("\n" + "=" * 60)
    print("ALL DATASETS PROCESSED")
    print("=" * 60)

    for report in reports:
        print(
            f"{report['dataset']}: "
            f"{report['records_before']} -> "
            f"{report['records_after']} records"
        )