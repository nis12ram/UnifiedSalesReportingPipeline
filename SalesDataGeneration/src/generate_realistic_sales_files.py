##### nis12ram

"""
GENERATES DAILY SALES DATA FOR NORTH, SOUTH & WEST REGIONAL BRANCHES
"""

import pandas as pd
import random, json, os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from product_prices import products_prices
from payment_methods import payment_methods
from customers import customers

products = list(products_prices.keys())


# IST timezone
IST = ZoneInfo("Asia/Kolkata")


# Function to generate a random IST datetime for a given date
def random_created_at(date_str: str, start_hour=9, end_hour=22) -> datetime:
    """
    date_str: 'YYYY-MM-DD'
    Returns a timezone-aware datetime in IST between start_hour and end_hour
    """
    # Base date at start_hour
    base_dt = datetime.strptime(date_str, "%Y-%m-%d").replace(
        hour=start_hour, minute=0, second=0, tzinfo=IST
    )

    # Random seconds to add (within the time window)
    delta_seconds = (end_hour - start_hour) * 3600
    random_seconds = random.randint(0, delta_seconds)

    return base_dt + timedelta(seconds=random_seconds)


def generate_data(
    root_path: str, rows: int = 1200
):  # -> dict[str, Any]:# -> dict[str, Any]:# -> dict[str, Any]:# -> dict[str, Any]:# -> dict[str, Any]:# -> dict[str, Any]:
    # ----------------------------
    # Settings
    # ----------------------------
    today = date.today()
    file_date = today.strftime("%Y-%m-%d")  ## today's date in yyyy-MM-dd format
    base_dir = os.path.join(root_path, file_date)

    try:
        os.makedirs(base_dir, exist_ok=False)
    except FileExistsError as _:
        raise Exception(f"Sales data for date: {file_date} already generated.")

    def save(df, name):
        path = os.path.join(base_dir, name)
        df.to_csv(path, index=False)
        print(f"Created {path}")
        return path

    # ----------------------------
    # NORTH:
    # ----------------------------
    north_data = []
    for i in range(rows):
        rand_product = random.choice(products * 20 + [None] + [""])
        sale_date = file_date  # yyyy-MM-dd
        created_at_dt = random_created_at(sale_date)

        north_data.append(
            {
                "SaleID": f"{random.randint(0, int(1e4))}",  # can contain duplicate SaleID & data type is string
                "SaleDate": sale_date,  # sale date in yyyy-mm-dd format
                "Customer": random.choice(
                    customers * 10 + [None] + [""]
                ),  # can contain empty or NULL value
                "Product": rand_product,  # can contain empty or NULL value
                "Units": random.choice(
                    list(range(2, 20)) * 100 + [-1, 0] + [None]
                ),  # can containe negative or zero value
                "UnitPrice": products_prices.get(
                    rand_product
                ),  # con contain NULL value
                "PaymentMethod": random.choice(
                    payment_methods * 50 + [None]
                ),  # can contain NULL value
                "CreatedAt": created_at_dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),  # timezone-aware datetime
            },
        )

    df_north = pd.DataFrame(north_data)
    north_file_name = f"North_Sales_{file_date}.csv"
    north_path = save(df_north, north_file_name)

    # ----------------------------
    # SOUTH:
    # ----------------------------
    south_data = []
    for i in range(rows):
        rand_product = random.choice(products * 20 + [None] + [""])
        sale_date = file_date  # yyyy-MM-dd
        created_at_dt = random_created_at(sale_date)

        south_data.append(
            {
                "TransactionID": random.randint(
                    0, int(1e4)
                ),  # can contain duplicate SaleID
                "TransactionDate": today.strftime(
                    "%m/%d/%Y"
                ),  # sale date in mm/dd/yyyy format
                "ClientName": random.choice(
                    customers * 10 + [None] + [""]
                ),  # can contain empty or NULL value
                "ItemName": rand_product,  # can contain empty or NULL value
                "QuantitySold": random.choice(
                    list(range(2, 20)) * 100 + [-1, 0] + [None]
                ),  # can containe negative or zero value
                "PricePerUnit": products_prices.get(
                    rand_product
                ),  # con contain NULL value
                "PaymentType": random.choice(
                    payment_methods * 50 + [None]
                ),  # can contain NULL value
                "RecordCreatedAt": created_at_dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),  # timezone-aware datetime
                "SourceSystem": random.choice(
                    ["POS", "ONLINE", "MOBILE", None]
                ),  # extra column
            }
        )

    df_south = pd.DataFrame(south_data)
    south_file_name = f"South_Sales_{file_date}.csv"
    south_path = save(df_south, south_file_name)

    # ----------------------------
    # WEST:
    # ----------------------------
    west_data = []
    for i in range(rows):
        rand_product = random.choice(products * 20 + [None] + [""])
        sale_date = file_date  # yyyy-MM-dd
        created_at_dt = random_created_at(sale_date)

        west_data.append(
            {
                "order_id": f"{random.randint(0, int(1e4))}",  # can contain duplicate SaleID & data type is in string
                "order_date": today.strftime(
                    "%m-%d-%Y"
                ),  # sale dae in mm-dd-yyyy format
                "buyer": random.choice(
                    customers * 10 + [None] + [""]
                ),  # can contain empty or NULL value
                "item": rand_product,  # can contain empty or NULL value
                "unit_count": random.choice(
                    list(range(2, 20)) * 100 + [-1, 0] + [None]
                ),  # can containe negative or zero value
                "unit_cost": products_prices.get(
                    rand_product
                ),  # con contain NULL value
                "payment_channel": random.choice(
                    payment_methods * 50 + [None]
                ),  # can contain NULL value
                "created_timestamp": created_at_dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),  # timezone-aware datetime
                "discount": random.choice(range(2, 40)),
            },
        )

    df_west = pd.DataFrame(west_data)
    west_file_name = f"West_Sales_{file_date}.csv"
    west_path = save(df_west, west_file_name)

    # ----------------------------
    # MANIFEST (audit & orchestration)
    # ----------------------------
    manifest = {
        "batch_date": file_date,
        "expected_files": 3,
        "files_path": {
            "north": north_path,
            "south": south_path,
            "west": west_path,
        },
        "files_name": {
            "north": north_file_name,
            "south": south_file_name,
            "west": west_file_name,
        },
    }

    manifest_path = os.path.join(base_dir, f"manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Created manifest {manifest_path}")
    return manifest
