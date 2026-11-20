from pathlib import Path
import pandas as pd

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SILVER_PATH = PROJECT_ROOT / "data" / "silver"
GOLD_PATH = PROJECT_ROOT / "data" / "gold"

CUSTOMERS_PATH = SILVER_PATH / "customers" / "customers.parquet"
ORDERS_PATH = SILVER_PATH / "orders" / "orders.parquet"
PRODUCTS_PATH = SILVER_PATH / "products" / "products.parquet"


# ============================================================
# GOLD OUTPUT PATHS
# ============================================================

CUSTOMER_GOLD_PATH = (
    GOLD_PATH / "customer_summary" / "customer_summary.parquet"
)

PRODUCT_GOLD_PATH = (
    GOLD_PATH / "product_summary" / "product_summary.parquet"
)

SALES_GOLD_PATH = (
    GOLD_PATH / "sales_summary" / "sales_summary.parquet"
)


# ============================================================
# LOAD SILVER DATA
# ============================================================

def load_silver_data():
    print("=" * 70)
    print("LOADING SILVER DATA")
    print("=" * 70)

    customers = pd.read_parquet(CUSTOMERS_PATH)
    orders = pd.read_parquet(ORDERS_PATH)
    products = pd.read_parquet(PRODUCTS_PATH)

    print(f"Customers loaded: {len(customers)}")
    print(f"Orders loaded:   {len(orders)}")
    print(f"Products loaded: {len(products)}")

    return customers, orders, products


# ============================================================
# CUSTOMER SUMMARY
# Grain: One row per customer
# ============================================================

def build_customer_summary(customers, orders):
    print("\n" + "=" * 70)
    print("BUILDING CUSTOMER SUMMARY")
    print("=" * 70)

    # Aggregate order metrics by customer
    customer_order_metrics = (
        orders.groupby("customer_id")
        .agg(
            total_orders=("order_id", "count"),
            last_order_date=("order_date", "max"),
        )
        .reset_index()
    )

    # Calculate order counts by status
    status_counts = (
        orders.pivot_table(
            index="customer_id",
            columns="order_status",
            values="order_id",
            aggfunc="count",
            fill_value=0,
        )
        .reset_index()
    )

    # Standardize status metric column names
    status_column_mapping = {
        "Delivered": "delivered_orders",
        "Cancelled": "cancelled_orders",
        "Returned": "returned_orders",
        "Shipped": "shipped_orders",
        "Processing": "processing_orders",
    }

    status_counts = status_counts.rename(
        columns=status_column_mapping
    )

    # Merge customer order metrics
    customer_summary = customers.merge(
        customer_order_metrics,
        on="customer_id",
        how="left",
    )

    customer_summary = customer_summary.merge(
        status_counts,
        on="customer_id",
        how="left",
    )

    # Fill missing order metrics for customers with no orders
    order_metric_columns = [
        "total_orders",
        "delivered_orders",
        "cancelled_orders",
        "returned_orders",
        "shipped_orders",
        "processing_orders",
    ]

    for column in order_metric_columns:
        if column not in customer_summary.columns:
            customer_summary[column] = 0

        customer_summary[column] = (
            customer_summary[column]
            .fillna(0)
            .astype("int64")
        )

    # Customer classification
    def classify_customer(row):
        if row["total_orders"] == 0:
            return "No Orders"

        if row["delivered_orders"] > 0:
            return "Delivered Customer"

        return "Active Customer"

    customer_summary["customer_order_status"] = (
        customer_summary.apply(
            classify_customer,
            axis=1,
        )
    )

    # Reorder columns
    customer_summary = customer_summary[
        [
            "customer_id",
            "customer_name",
            "email",
            "city",
            "region",
            "signup_date",
            "total_orders",
            "delivered_orders",
            "cancelled_orders",
            "returned_orders",
            "shipped_orders",
            "processing_orders",
            "last_order_date",
            "customer_order_status",
        ]
    ]

    # Save Gold dataset
    CUSTOMER_GOLD_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    customer_summary.to_parquet(
        CUSTOMER_GOLD_PATH,
        index=False,
    )

    print(f"Customer summary records: {len(customer_summary)}")
    print(f"Saved to: {CUSTOMER_GOLD_PATH}")

    return customer_summary


# ============================================================
# PRODUCT SUMMARY
# Grain: One row per product
# ============================================================

def build_product_summary(products):
    print("\n" + "=" * 70)
    print("BUILDING PRODUCT SUMMARY")
    print("=" * 70)

    product_summary = products.copy()

    # Calculate inventory value
    product_summary["inventory_value"] = (
        product_summary["price"]
        * product_summary["stock_quantity"]
    )

    # Classify inventory
    def classify_stock(stock_quantity):
        if stock_quantity == 0:
            return "Out of Stock"

        elif stock_quantity <= 10:
            return "Low Stock"

        return "In Stock"

    product_summary["stock_status"] = (
        product_summary["stock_quantity"]
        .apply(classify_stock)
    )

    # Save Gold dataset
    PRODUCT_GOLD_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    product_summary.to_parquet(
        PRODUCT_GOLD_PATH,
        index=False,
    )

    print(f"Product summary records: {len(product_summary)}")
    print(f"Saved to: {PRODUCT_GOLD_PATH}")

    return product_summary


# ============================================================
# SALES SUMMARY
# Grain: One row per order date + order status
# ============================================================

def build_sales_summary(orders):
    print("\n" + "=" * 70)
    print("BUILDING SALES SUMMARY")
    print("=" * 70)

    # Aggregate orders by date and status
    sales_summary = (
        orders.groupby(
            ["order_date", "order_status"],
            as_index=False,
        )
        .agg(
            total_orders=("order_id", "count"),
            unique_customers=("customer_id", "nunique"),
        )
    )

    # Calculate total orders per date
    daily_totals = (
        orders.groupby("order_date")
        .agg(
            daily_total_orders=("order_id", "count"),
        )
        .reset_index()
    )

    # Merge daily totals into date/status summary
    sales_summary = sales_summary.merge(
        daily_totals,
        on="order_date",
        how="left",
    )

    # Calculate status percentage of daily orders
    sales_summary["percentage_of_daily_orders"] = (
        sales_summary["total_orders"]
        / sales_summary["daily_total_orders"]
        * 100
    )

    # Sort output
    sales_summary = sales_summary.sort_values(
        ["order_date", "order_status"]
    ).reset_index(drop=True)

    # Save Gold dataset
    SALES_GOLD_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    sales_summary.to_parquet(
        SALES_GOLD_PATH,
        index=False,
    )

    print(f"Sales summary records: {len(sales_summary)}")
    print(f"Saved to: {SALES_GOLD_PATH}")

    return sales_summary


# ============================================================
# GOLD LAYER SUMMARY
# ============================================================

def print_gold_summary(
    customer_summary,
    product_summary,
    sales_summary,
):
    print("\n" + "=" * 70)
    print("GOLD LAYER TRANSFORMATION SUMMARY")
    print("=" * 70)

    print("\nGold datasets generated:")
    print(
        f"customer_summary: "
        f"{len(customer_summary)} records"
    )

    print(
        f"product_summary: "
        f"{len(product_summary)} records"
    )

    print(
        f"sales_summary: "
        f"{len(sales_summary)} records"
    )

    print("\nCustomer classifications:")
    print(
        customer_summary[
            "customer_order_status"
        ].value_counts().to_string()
    )

    print("\nProduct stock classifications:")
    print(
        product_summary[
            "stock_status"
        ].value_counts().to_string()
    )

    print("\nOrder status distribution:")
    print(
        sales_summary.groupby("order_status")[
            "total_orders"
        ].sum().to_string()
    )

    print("\nTotal orders represented in Gold sales summary:")
    print(
        sales_summary["total_orders"].sum()
    )

    print("\nGold output locations:")
    print(f"Customers: {CUSTOMER_GOLD_PATH}")
    print(f"Products:  {PRODUCT_GOLD_PATH}")
    print(f"Sales:     {SALES_GOLD_PATH}")

    print("\n" + "=" * 70)
    print("GOLD LAYER BUILD COMPLETED")
    print("=" * 70)


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():
    # Load Silver datasets
    customers, orders, products = load_silver_data()

    # Build Gold datasets
    customer_summary = build_customer_summary(
        customers,
        orders,
    )

    product_summary = build_product_summary(
        products,
    )

    sales_summary = build_sales_summary(
        orders,
    )

    # Print summary
    print_gold_summary(
        customer_summary,
        product_summary,
        sales_summary,
    )


if __name__ == "__main__":
    main()