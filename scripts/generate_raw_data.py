
import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw

# =========================================================
# PROJECT CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

CSV_DIR = RAW_DIR / "csv"
JSON_DIR = RAW_DIR / "json"
LOG_DIR = RAW_DIR / "logs"
TEXT_DIR = RAW_DIR / "text"
IMAGE_DIR = RAW_DIR / "images"

random.seed(42)

# =========================================================
# CREATE DIRECTORIES
# =========================================================

for directory in [CSV_DIR, JSON_DIR, LOG_DIR, TEXT_DIR, IMAGE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# =========================================================
# SAMPLE VALUES
# =========================================================

first_names = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Rohan",
    "Ananya", "Priya", "Neha", "Isha", "Meera",
    "Kabir", "Rahul", "Sanya", "Aditi", "Karan"
]

last_names = [
    "Sharma", "Verma", "Singh", "Gupta", "Patel",
    "Kumar", "Malhotra", "Mehta", "Kapoor", "Das"
]

cities = [
    "Delhi", "Mumbai", "Chandigarh", "Panchkula",
    "Bengaluru", "Hyderabad", "Pune", "Jaipur"
]

regions = ["North", "South", "East", "West"]

# =========================================================
# GENERATE CUSTOMERS
# =========================================================

customers = []

for customer_id in range(1, 101):
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)

    customers.append({
        "customer_id": customer_id,
        "customer_name": f"{first_name} {last_name}",
        "email": f"customer{customer_id}@example.com",
        "city": random.choice(cities),
        "region": random.choice(regions),
        "signup_date": (
            datetime(2025, 1, 1)
            + timedelta(days=random.randint(0, 365))
        ).strftime("%Y-%m-%d")
    })

# =========================================================
# GENERATE PRODUCTS
# =========================================================

products = []

product_names = [
    "Laptop", "Smartphone", "Tablet", "Monitor",
    "Keyboard", "Mouse", "Headphones", "Smartwatch",
    "Camera", "Printer", "Speaker", "Router",
    "External SSD", "Power Bank", "Webcam"
]

categories = ["Electronics", "Accessories", "Computing"]

for product_id in range(1, 31):
    product_name = random.choice(product_names)

    products.append({
        "product_id": product_id,
        "product_name": f"{product_name} Model {product_id}",
        "category": random.choice(categories),
        "price": round(random.uniform(500, 80000), 2),
        "stock_quantity": random.randint(0, 200)
    })

# =========================================================
# GENERATE ORDERS
# =========================================================

orders = []

statuses = [
    "Delivered", "Shipped", "Processing",
    "Cancelled", "Returned"
]

payment_methods = [
    "Credit Card", "Debit Card", "UPI",
    "Net Banking", "Cash on Delivery"
]

for order_id in range(1, 251):
    order_date = (
        datetime(2025, 1, 1)
        + timedelta(days=random.randint(0, 365))
    )

    orders.append({
        "order_id": order_id,
        "customer_id": random.randint(1, 100),
        "order_date": order_date.strftime("%Y-%m-%d"),
        "order_status": random.choice(statuses),
        "payment_method": random.choice(payment_methods)
    })

# =========================================================
# CSV WRITING FUNCTION
# =========================================================

def write_csv(filename, records):
    filepath = CSV_DIR / filename

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(records[0].keys())
        )

        writer.writeheader()
        writer.writerows(records)

    print(f"Created CSV: {filename} ({len(records)} records)")

# =========================================================
# WRITE CSV FILES
# =========================================================

write_csv("customers.csv", customers)
write_csv("products.csv", products)
write_csv("orders.csv", orders)

# =========================================================
# GENERATE CUSTOMER EVENTS JSON
# =========================================================

customer_events = []

event_types = [
    "login", "product_view", "add_to_cart",
    "purchase", "logout"
]

devices = ["mobile", "desktop", "tablet"]

for event_id in range(1, 101):
    event_time = (
        datetime(2025, 1, 1, 8, 0, 0)
        + timedelta(minutes=random.randint(0, 500000))
    )

    customer_events.append({
        "event_id": event_id,
        "customer_id": random.randint(1, 100),
        "event_type": random.choice(event_types),
        "event_timestamp": event_time.isoformat(),
        "device": random.choice(devices),
        "metadata": {
            "source": random.choice(["website", "mobile_app"]),
            "session_id": f"SESSION-{random.randint(1000, 9999)}"
        }
    })

with open(JSON_DIR / "customer_events.json", "w", encoding="utf-8") as file:
    json.dump(customer_events, file, indent=4)

print(f"Created JSON: customer_events.json ({len(customer_events)} records)")

# =========================================================
# GENERATE NESTED PRODUCT CATALOG JSON
# =========================================================

product_catalog = {
    "catalog_name": "E-Commerce Product Catalog",
    "generated_at": datetime.now().isoformat(),
    "catalog_version": "1.0",
    "products": []
}

for product in products:
    product_catalog["products"].append({
        "product_id": product["product_id"],
        "name": product["product_name"],
        "category": product["category"],
        "pricing": {
            "currency": "INR",
            "amount": product["price"]
        },
        "inventory": {
            "available_quantity": product["stock_quantity"],
            "status": (
                "In Stock"
                if product["stock_quantity"] > 0
                else "Out of Stock"
            )
        }
    })

with open(JSON_DIR / "product_catalog.json", "w", encoding="utf-8") as file:
    json.dump(product_catalog, file, indent=4)

print("Created JSON: product_catalog.json")

# =========================================================
# GENERATE APPLICATION LOGS
# =========================================================

log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]

log_messages = [
    "Application started",
    "User login successful",
    "Product page viewed",
    "Order created successfully",
    "Payment processing initiated",
    "Payment completed",
    "Inventory updated",
    "Session terminated",
    "Request timeout",
    "Database connection failed"
]

with open(LOG_DIR / "application.log", "w", encoding="utf-8") as file:
    start_time = datetime(2025, 1, 1, 9, 0, 0)

    for log_id in range(1, 201):
        timestamp = start_time + timedelta(seconds=log_id * 30)
        level = random.choice(log_levels)
        message = random.choice(log_messages)

        file.write(
            f"{timestamp.isoformat()} "
            f"[{level}] "
            f"event_id={log_id} "
            f"{message}\n"
        )

print("Created log: application.log (200 records)")

# =========================================================
# GENERATE BUSINESS NOTES
# =========================================================

business_notes = """
E-COMMERCE BUSINESS NOTES

The business operates an online retail platform.

Customers can browse products, place orders, make payments,
and track shipments.

The platform supports multiple product categories.

Customer behavior data is collected through website and
mobile application events.

Sales teams analyze order performance and customer activity.

Data engineering teams process raw information to support
business reporting and analytics.
"""

with open(TEXT_DIR / "business_notes.txt", "w", encoding="utf-8") as file:
    file.write(business_notes.strip())

# =========================================================
# GENERATE DATA DICTIONARY
# =========================================================

data_dictionary = """
DATA DICTIONARY

CUSTOMERS
customer_id      Unique customer identifier
customer_name    Customer full name
email            Customer email
city             Customer city
region            Geographic region
signup_date       Customer registration date

PRODUCTS
product_id        Unique product identifier
product_name      Product name
category          Product category
price             Product price in INR
stock_quantity    Current inventory quantity

ORDERS
order_id          Unique order identifier
customer_id       Customer associated with order
order_date        Order creation date
order_status      Current order status
payment_method    Payment method used
"""

with open(TEXT_DIR / "data_dictionary.txt", "w", encoding="utf-8") as file:
    file.write(data_dictionary.strip())

print("Created text files: business_notes.txt and data_dictionary.txt")

# =========================================================
# GENERATE SAMPLE IMAGE
# =========================================================

image = Image.new("RGB", (800, 600), "#F2F4F7")
draw = ImageDraw.Draw(image)

draw.rounded_rectangle(
    (250, 120, 550, 440),
    radius=30,
    fill="#2D3748"
)

draw.rounded_rectangle(
    (280, 150, 520, 390),
    radius=15,
    fill="#63B3ED"
)

draw.rectangle(
    (220, 440, 580, 475),
    fill="#718096"
)

draw.text(
    (300, 510),
    "Sample Data Lake Product Image",
    fill="#1A202C"
)

image.save(IMAGE_DIR / "sample_product.png")

print("Created image: sample_product.png")

# =========================================================
# FINAL SUMMARY
# =========================================================

print("\n======================================")
print("RAW DATA GENERATION COMPLETED")
print("======================================")

print(f"Customers: {len(customers)}")
print(f"Products: {len(products)}")
print(f"Orders: {len(orders)}")
print(f"Customer events: {len(customer_events)}")
print("Application log records: 200")

print("\nFiles generated successfully.")
print(f"Raw data location: {RAW_DIR}")
