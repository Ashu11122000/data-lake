from pathlib import Path
import pandas as pd

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SILVER_PATH = PROJECT_ROOT / "data" / "silver"
GOLD_PATH = PROJECT_ROOT / "data" / "gold"

SILVER_CUSTOMERS = SILVER_PATH / "customers" / "customers.parquet"
SILVER_ORDERS = SILVER_PATH / "orders" / "orders.parquet"
SILVER_PRODUCTS = SILVER_PATH / "products" / "products.parquet"

GOLD_CUSTOMERS = GOLD_PATH / "customer_summary" / "customer_summary.parquet"
GOLD_PRODUCTS = GOLD_PATH / "product_summary" / "product_summary.parquet"
GOLD_SALES = GOLD_PATH / "sales_summary" / "sales_summary.parquet"


# ============================================================
# VALIDATION HELPER
# ============================================================

total_checks = 0
failed_checks = 0


def check(name, condition, details=""):
    global total_checks, failed_checks

    total_checks += 1

    if condition:
        status = "PASS"
    else:
        status = "FAIL"
        failed_checks += 1

    print(f"[{status}] {name}")

    if details:
        print(f"       {details}")


# ============================================================
# LOAD DATA
# ============================================================

def load_datasets():
    print("=" * 70)
    print("LOADING SILVER AND GOLD DATASETS")
    print("=" * 70)

    silver_customers = pd.read_parquet(SILVER_CUSTOMERS)
    silver_orders = pd.read_parquet(SILVER_ORDERS)
    silver_products = pd.read_parquet(SILVER_PRODUCTS)

    gold_customers = pd.read_parquet(GOLD_CUSTOMERS)
    gold_products = pd.read_parquet(GOLD_PRODUCTS)
    gold_sales = pd.read_parquet(GOLD_SALES)

    print("\nSilver datasets:")
    print(f"Customers: {len(silver_customers)}")
    print(f"Orders:   {len(silver_orders)}")
    print(f"Products: {len(silver_products)}")

    print("\nGold datasets:")
    print(f"Customer summary: {len(gold_customers)}")
    print(f"Product summary:  {len(gold_products)}")
    print(f"Sales summary:    {len(gold_sales)}")

    return (
        silver_customers,
        silver_orders,
        silver_products,
        gold_customers,
        gold_products,
        gold_sales,
    )


# ============================================================
# CUSTOMER GOLD VALIDATION
# ============================================================

def validate_customer_gold(
    silver_customers,
    silver_orders,
    gold_customers,
):
    print("\n" + "=" * 70)
    print("CUSTOMER GOLD VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Record count
    # --------------------------------------------------------

    check(
        "Customer Gold record count matches Silver customers",
        len(gold_customers) == len(silver_customers),
        f"Silver: {len(silver_customers)}, Gold: {len(gold_customers)}",
    )

    # --------------------------------------------------------
    # Unique customer IDs
    # --------------------------------------------------------

    check(
        "Customer Gold customer_id is unique",
        gold_customers["customer_id"].is_unique,
    )

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------
    # last_order_date is allowed to be null for customers
    # who have never placed an order.

    columns_required = [
        column
        for column in gold_customers.columns
        if column != "last_order_date"
    ]

    missing_required_values = (
        gold_customers[columns_required]
        .isna()
        .sum()
        .sum()
    )

    check(
        "Customer Gold required columns contain no missing values",
        missing_required_values == 0,
        f"Missing required values: {missing_required_values}",
    )

    # --------------------------------------------------------
    # Validate last_order_date null values
    # --------------------------------------------------------
    # A null last_order_date is valid only when total_orders = 0.

    null_last_order_dates = (
        gold_customers["last_order_date"].isna()
    )

    null_date_customers_with_orders = (
        null_last_order_dates
        & (gold_customers["total_orders"] > 0)
    ).sum()

    check(
        "Null last_order_date is only present for customers with no orders",
        null_date_customers_with_orders == 0,
        f"Invalid null dates: {null_date_customers_with_orders}",
    )

    # --------------------------------------------------------
    # Customer order totals
    # --------------------------------------------------------

    silver_customer_order_counts = (
        silver_orders.groupby("customer_id")
        .size()
        .to_dict()
    )

    gold_customer_order_counts = (
        gold_customers.set_index("customer_id")["total_orders"]
        .to_dict()
    )

    mismatched_customers = 0

    for customer_id in gold_customers["customer_id"]:

        expected = silver_customer_order_counts.get(
            customer_id,
            0,
        )

        actual = gold_customer_order_counts.get(
            customer_id,
            0,
        )

        if expected != actual:
            mismatched_customers += 1

    check(
        "Customer order counts match Silver orders",
        mismatched_customers == 0,
        f"Mismatched customers: {mismatched_customers}",
    )

    # --------------------------------------------------------
    # Total order reconciliation
    # --------------------------------------------------------

    gold_total_orders = gold_customers["total_orders"].sum()
    silver_total_orders = len(silver_orders)

    check(
        "Customer Gold total orders reconcile with Silver",
        gold_total_orders == silver_total_orders,
        f"Silver: {silver_total_orders}, Gold: {gold_total_orders}",
    )

    # --------------------------------------------------------
    # Customer classification validation
    # --------------------------------------------------------

    expected_classifications = []

    for _, row in gold_customers.iterrows():

        if row["total_orders"] == 0:
            expected = "No Orders"

        elif row["delivered_orders"] > 0:
            expected = "Delivered Customer"

        else:
            expected = "Active Customer"

        expected_classifications.append(expected)

    classification_mismatches = (
        gold_customers["customer_order_status"]
        != expected_classifications
    ).sum()

    check(
        "Customer classifications follow transformation logic",
        classification_mismatches == 0,
        f"Mismatches: {classification_mismatches}",
    )

    # --------------------------------------------------------
    # Status totals
    # --------------------------------------------------------

    customer_status_columns = [
        "delivered_orders",
        "cancelled_orders",
        "returned_orders",
        "shipped_orders",
        "processing_orders",
    ]

    gold_status_total = (
        gold_customers[customer_status_columns]
        .sum()
        .sum()
    )

    check(
        "Customer status totals reconcile with Silver orders",
        gold_status_total == silver_total_orders,
        f"Silver orders: {silver_total_orders}, "
        f"Gold status totals: {gold_status_total}",
    )


# ============================================================
# PRODUCT GOLD VALIDATION
# ============================================================

def validate_product_gold(
    silver_products,
    gold_products,
):
    print("\n" + "=" * 70)
    print("PRODUCT GOLD VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Record count
    # --------------------------------------------------------

    check(
        "Product Gold record count matches Silver",
        len(gold_products) == len(silver_products),
        f"Silver: {len(silver_products)}, Gold: {len(gold_products)}",
    )

    # --------------------------------------------------------
    # Unique IDs
    # --------------------------------------------------------

    check(
        "Product Gold product_id is unique",
        gold_products["product_id"].is_unique,
    )

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    missing_count = gold_products.isna().sum().sum()

    check(
        "Product Gold contains no missing values",
        missing_count == 0,
        f"Missing values: {missing_count}",
    )

    # --------------------------------------------------------
    # Inventory value calculation
    # --------------------------------------------------------

    expected_inventory_value = (
        gold_products["price"]
        * gold_products["stock_quantity"]
    )

    inventory_value_mismatches = (
        gold_products["inventory_value"]
        - expected_inventory_value
    ).abs() > 0.000001

    mismatch_count = inventory_value_mismatches.sum()

    check(
        "Inventory value calculations are correct",
        mismatch_count == 0,
        f"Mismatches: {mismatch_count}",
    )

    # --------------------------------------------------------
    # Stock classification validation
    # --------------------------------------------------------

    expected_stock_status = []

    for quantity in gold_products["stock_quantity"]:

        if quantity == 0:
            status = "Out of Stock"

        elif quantity <= 10:
            status = "Low Stock"

        else:
            status = "In Stock"

        expected_stock_status.append(status)

    stock_status_mismatches = (
        gold_products["stock_status"]
        != expected_stock_status
    ).sum()

    check(
        "Stock classifications follow transformation logic",
        stock_status_mismatches == 0,
        f"Mismatches: {stock_status_mismatches}",
    )

    # --------------------------------------------------------
    # Product identity consistency
    # --------------------------------------------------------

    silver_product_ids = set(
        silver_products["product_id"]
    )

    gold_product_ids = set(
        gold_products["product_id"]
    )

    check(
        "Gold product IDs match Silver product IDs",
        silver_product_ids == gold_product_ids,
    )

    # --------------------------------------------------------
    # Total inventory reconciliation
    # --------------------------------------------------------

    check(
        "Total stock quantity matches Silver",
        gold_products["stock_quantity"].sum()
        == silver_products["stock_quantity"].sum(),
    )


# ============================================================
# SALES GOLD VALIDATION
# ============================================================

def validate_sales_gold(
    silver_orders,
    gold_sales,
):
    print("\n" + "=" * 70)
    print("SALES GOLD VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Grain uniqueness
    # --------------------------------------------------------

    duplicate_grain_count = gold_sales.duplicated(
        subset=["order_date", "order_status"]
    ).sum()

    check(
        "Sales Gold date + status grain is unique",
        duplicate_grain_count == 0,
        f"Duplicate combinations: {duplicate_grain_count}",
    )

    # --------------------------------------------------------
    # Total order reconciliation
    # --------------------------------------------------------

    gold_total_orders = gold_sales["total_orders"].sum()
    silver_total_orders = len(silver_orders)

    check(
        "Sales Gold total orders reconcile with Silver",
        gold_total_orders == silver_total_orders,
        f"Silver: {silver_total_orders}, Gold: {gold_total_orders}",
    )

    # --------------------------------------------------------
    # Daily total consistency
    # --------------------------------------------------------

    daily_total_mismatches = 0

    for order_date, group in gold_sales.groupby("order_date"):

        calculated_daily_total = (
            group["total_orders"].sum()
        )

        stored_daily_total = (
            group["daily_total_orders"].iloc[0]
        )

        if calculated_daily_total != stored_daily_total:
            daily_total_mismatches += 1

    check(
        "Daily total orders are consistent",
        daily_total_mismatches == 0,
        f"Dates with mismatches: {daily_total_mismatches}",
    )

    # --------------------------------------------------------
    # Percentage consistency
    # --------------------------------------------------------

    percentage_mismatches = 0

    for order_date, group in gold_sales.groupby("order_date"):

        percentage_total = (
            group["percentage_of_daily_orders"].sum()
        )

        if abs(percentage_total - 100) > 0.0001:
            percentage_mismatches += 1

    check(
        "Daily order-status percentages sum to 100%",
        percentage_mismatches == 0,
        f"Dates with mismatches: {percentage_mismatches}",
    )

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    missing_count = gold_sales.isna().sum().sum()

    check(
        "Sales Gold contains no missing values",
        missing_count == 0,
        f"Missing values: {missing_count}",
    )

    # --------------------------------------------------------
    # Status totals reconciliation
    # --------------------------------------------------------

    silver_status_totals = (
        silver_orders["order_status"]
        .value_counts()
        .sort_index()
    )

    gold_status_totals = (
        gold_sales.groupby("order_status")["total_orders"]
        .sum()
        .sort_index()
    )

    status_mismatches = 0

    all_statuses = set(silver_status_totals.index).union(
        set(gold_status_totals.index)
    )

    for status in all_statuses:

        silver_count = silver_status_totals.get(
            status,
            0,
        )

        gold_count = gold_status_totals.get(
            status,
            0,
        )

        if silver_count != gold_count:
            status_mismatches += 1

    check(
        "Order status totals match Silver",
        status_mismatches == 0,
        f"Status mismatches: {status_mismatches}",
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

def print_final_summary():
    print("\n" + "=" * 70)
    print("GOLD DATA QUALITY VALIDATION SUMMARY")
    print("=" * 70)

    print(f"Total checks: {total_checks}")
    print(f"Failed checks: {failed_checks}")
    print(f"Passed checks: {total_checks - failed_checks}")

    if failed_checks == 0:
        print("\nRESULT: ALL GOLD VALIDATION CHECKS PASSED")
    else:
        print("\nRESULT: GOLD VALIDATION FAILED")

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():
    datasets = load_datasets()

    (
        silver_customers,
        silver_orders,
        silver_products,
        gold_customers,
        gold_products,
        gold_sales,
    ) = datasets

    validate_customer_gold(
        silver_customers,
        silver_orders,
        gold_customers,
    )

    validate_product_gold(
        silver_products,
        gold_products,
    )

    validate_sales_gold(
        silver_orders,
        gold_sales,
    )

    print_final_summary()


if __name__ == "__main__":
    main()