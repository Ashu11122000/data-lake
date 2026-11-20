from pathlib import Path
import pandas as pd
import re

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SILVER_PATH = PROJECT_ROOT / "data" / "silver"

CUSTOMERS_PATH = SILVER_PATH / "customers" / "customers.parquet"
ORDERS_PATH = SILVER_PATH / "orders" / "orders.parquet"
PRODUCTS_PATH = SILVER_PATH / "products" / "products.parquet"


# ============================================================
# LOAD SILVER DATA
# ============================================================

def load_data():
    customers = pd.read_parquet(CUSTOMERS_PATH)
    orders = pd.read_parquet(ORDERS_PATH)
    products = pd.read_parquet(PRODUCTS_PATH)

    return customers, orders, products


# ============================================================
# VALIDATION HELPERS
# ============================================================

def print_check(name, count, passed):
    status = "PASS" if passed else "FAIL"

    print(
        f"[{status}] {name}: {count}"
    )


def validate_unique_ids(df, column_name, dataset_name):
    duplicate_count = df[column_name].duplicated().sum()

    print_check(
        f"{dataset_name} duplicate {column_name}",
        duplicate_count,
        duplicate_count == 0
    )

    return duplicate_count


def validate_missing_values(df, dataset_name):
    missing_count = df.isna().sum().sum()

    print_check(
        f"{dataset_name} total missing values",
        missing_count,
        missing_count == 0
    )

    return missing_count


# ============================================================
# CUSTOMER VALIDATION
# ============================================================

def validate_customers(customers):
    print("\n" + "=" * 70)
    print("CUSTOMER DATA QUALITY")
    print("=" * 70)

    duplicate_ids = validate_unique_ids(
        customers,
        "customer_id",
        "Customers"
    )

    missing_values = validate_missing_values(
        customers,
        "Customers"
    )

    # Validate email format
    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    invalid_emails = (
        ~customers["email"].astype(str).str.match(
            email_pattern,
            na=False
        )
    ).sum()

    print_check(
        "Invalid email addresses",
        invalid_emails,
        invalid_emails == 0
    )

    # Validate customer IDs
    invalid_customer_ids = (
        customers["customer_id"].isna()
        | (customers["customer_id"] <= 0)
    ).sum()

    print_check(
        "Invalid customer IDs",
        invalid_customer_ids,
        invalid_customer_ids == 0
    )

    # Validate signup dates
    invalid_signup_dates = (
        customers["signup_date"].isna()
    ).sum()

    print_check(
        "Invalid or missing signup dates",
        invalid_signup_dates,
        invalid_signup_dates == 0
    )

    # Check future signup dates
    today = pd.Timestamp.today().normalize()

    future_signup_dates = (
        customers["signup_date"] > today
    ).sum()

    print_check(
        "Future signup dates",
        future_signup_dates,
        future_signup_dates == 0
    )

    return {
        "duplicate_ids": duplicate_ids,
        "missing_values": missing_values,
        "invalid_emails": invalid_emails,
        "invalid_ids": invalid_customer_ids,
        "invalid_dates": invalid_signup_dates,
        "future_dates": future_signup_dates,
    }


# ============================================================
# ORDER VALIDATION
# ============================================================

def validate_orders(orders, customers):
    print("\n" + "=" * 70)
    print("ORDER DATA QUALITY")
    print("=" * 70)

    duplicate_ids = validate_unique_ids(
        orders,
        "order_id",
        "Orders"
    )

    missing_values = validate_missing_values(
        orders,
        "Orders"
    )

    # Validate order IDs
    invalid_order_ids = (
        orders["order_id"].isna()
        | (orders["order_id"] <= 0)
    ).sum()

    print_check(
        "Invalid order IDs",
        invalid_order_ids,
        invalid_order_ids == 0
    )

    # Validate customer IDs referenced by orders
    customer_id_set = set(
        customers["customer_id"].dropna()
    )

    invalid_customer_references = (
        ~orders["customer_id"].isin(customer_id_set)
    ).sum()

    print_check(
        "Orders with customer IDs not found in Customers",
        invalid_customer_references,
        invalid_customer_references == 0
    )

    # Validate order dates
    invalid_order_dates = (
        orders["order_date"].isna()
    ).sum()

    print_check(
        "Missing or invalid order dates",
        invalid_order_dates,
        invalid_order_dates == 0
    )

    # Future order dates
    today = pd.Timestamp.today().normalize()

    future_order_dates = (
        orders["order_date"] > today
    ).sum()

    print_check(
        "Future order dates",
        future_order_dates,
        future_order_dates == 0
    )

    # Check blank statuses
    invalid_statuses = (
        orders["order_status"].isna()
        | (
            orders["order_status"]
            .astype(str)
            .str.strip()
            .eq("")
        )
    ).sum()

    print_check(
        "Missing order statuses",
        invalid_statuses,
        invalid_statuses == 0
    )

    # Check blank payment methods
    invalid_payment_methods = (
        orders["payment_method"].isna()
        | (
            orders["payment_method"]
            .astype(str)
            .str.strip()
            .eq("")
        )
    ).sum()

    print_check(
        "Missing payment methods",
        invalid_payment_methods,
        invalid_payment_methods == 0
    )

    # Show categories currently present in the dataset
    print("\nOrder status values found:")
    print(
        orders["order_status"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nPayment methods found:")
    print(
        orders["payment_method"]
        .value_counts(dropna=False)
        .to_string()
    )

    return {
        "duplicate_ids": duplicate_ids,
        "missing_values": missing_values,
        "invalid_order_ids": invalid_order_ids,
        "invalid_customer_references": invalid_customer_references,
        "invalid_dates": invalid_order_dates,
        "future_dates": future_order_dates,
        "missing_statuses": invalid_statuses,
        "missing_payment_methods": invalid_payment_methods,
    }


# ============================================================
# PRODUCT VALIDATION
# ============================================================

def validate_products(products):
    print("\n" + "=" * 70)
    print("PRODUCT DATA QUALITY")
    print("=" * 70)

    duplicate_ids = validate_unique_ids(
        products,
        "product_id",
        "Products"
    )

    missing_values = validate_missing_values(
        products,
        "Products"
    )

    # Validate product IDs
    invalid_product_ids = (
        products["product_id"].isna()
        | (products["product_id"] <= 0)
    ).sum()

    print_check(
        "Invalid product IDs",
        invalid_product_ids,
        invalid_product_ids == 0
    )

    # Validate prices
    invalid_prices = (
        products["price"].isna()
        | (products["price"] < 0)
    ).sum()

    print_check(
        "Invalid or negative prices",
        invalid_prices,
        invalid_prices == 0
    )

    # Validate inventory
    invalid_stock = (
        products["stock_quantity"].isna()
        | (products["stock_quantity"] < 0)
    ).sum()

    print_check(
        "Invalid or negative stock quantities",
        invalid_stock,
        invalid_stock == 0
    )

    # Validate product names
    invalid_names = (
        products["product_name"].isna()
        | (
            products["product_name"]
            .astype(str)
            .str.strip()
            .eq("")
        )
    ).sum()

    print_check(
        "Missing product names",
        invalid_names,
        invalid_names == 0
    )

    # Validate categories
    invalid_categories = (
        products["category"].isna()
        | (
            products["category"]
            .astype(str)
            .str.strip()
            .eq("")
        )
    ).sum()

    print_check(
        "Missing product categories",
        invalid_categories,
        invalid_categories == 0
    )

    return {
        "duplicate_ids": duplicate_ids,
        "missing_values": missing_values,
        "invalid_product_ids": invalid_product_ids,
        "invalid_prices": invalid_prices,
        "invalid_stock": invalid_stock,
        "invalid_names": invalid_names,
        "invalid_categories": invalid_categories,
    }


# ============================================================
# OVERALL SUMMARY
# ============================================================

def generate_summary(results):
    total_issues = 0

    for dataset_results in results.values():
        total_issues += sum(dataset_results.values())

    print("\n" + "=" * 70)
    print("OVERALL DATA QUALITY SUMMARY")
    print("=" * 70)

    for dataset_name, dataset_results in results.items():

        dataset_issues = sum(
            dataset_results.values()
        )

        status = (
            "PASS"
            if dataset_issues == 0
            else "FAIL"
        )

        print(
            f"{dataset_name.upper():<15} "
            f"{status:<10} "
            f"Issues: {dataset_issues}"
        )

    print("-" * 70)
    print(f"Total data quality issues: {total_issues}")

    if total_issues == 0:
        print("RESULT: ALL DATA QUALITY CHECKS PASSED")
    else:
        print("RESULT: DATA QUALITY ISSUES DETECTED")

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("SILVER DATA QUALITY VALIDATION")
    print("=" * 70)

    customers, orders, products = load_data()

    print("\nDatasets loaded successfully:")
    print(f"Customers: {len(customers)} records")
    print(f"Orders:   {len(orders)} records")
    print(f"Products: {len(products)} records")

    customer_results = validate_customers(customers)

    order_results = validate_orders(
        orders,
        customers
    )

    product_results = validate_products(products)

    results = {
        "customers": customer_results,
        "orders": order_results,
        "products": product_results,
    }

    generate_summary(results)


if __name__ == "__main__":
    main()