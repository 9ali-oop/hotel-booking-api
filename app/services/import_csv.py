"""
CSV import script for loading the Hotel Booking Demand dataset into SQLite.

This script reads the Kaggle CSV file and bulk-inserts all 119,390 records
into the bookings table. It handles NULL values from the CSV (encoded as
the string "NULL") and converts them appropriately.

Usage:
    python -m app.services.import_csv
"""

import csv
import os
import sys
from datetime import datetime

# Add project root to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import engine, SessionLocal, Base
from app.models import Booking


def clean_value(value: str, field_type: str = "str"):
    """
    Clean a CSV field value. The dataset uses the string 'NULL'
    for missing values, which we convert to Python None.
    """
    if value is None or value.strip() == "" or value.strip().upper() == "NULL":
        return None

    if field_type == "int":
        try:
            # Some fields like 'children' have values like '0.0'
            return int(float(value))
        except (ValueError, TypeError):
            return None
    elif field_type == "float":
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    return value.strip()


def import_csv(csv_path: str = None):
    """
    Import the hotel bookings CSV into the database.
    Creates all tables if they don't exist, then bulk-inserts records.
    """
    if csv_path is None:
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data",
            "hotel_bookings.csv"
        )

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Check if data already exists
    existing_count = db.query(Booking).count()
    if existing_count > 0:
        print(f"Database already contains {existing_count} bookings. Skipping import.")
        print("To reimport, delete hotel_bookings.db and run again.")
        db.close()
        return

    print(f"Reading CSV from {csv_path}...")

    bookings = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            booking = Booking(
                hotel=clean_value(row["hotel"]),
                is_canceled=clean_value(row["is_canceled"], "int"),
                lead_time=clean_value(row["lead_time"], "int"),
                arrival_date_year=clean_value(row["arrival_date_year"], "int"),
                arrival_date_month=clean_value(row["arrival_date_month"]),
                arrival_date_week_number=clean_value(row["arrival_date_week_number"], "int"),
                arrival_date_day_of_month=clean_value(row["arrival_date_day_of_month"], "int"),
                stays_in_weekend_nights=clean_value(row["stays_in_weekend_nights"], "int"),
                stays_in_week_nights=clean_value(row["stays_in_week_nights"], "int"),
                adults=clean_value(row["adults"], "int"),
                children=clean_value(row["children"], "int"),
                babies=clean_value(row["babies"], "int"),
                meal=clean_value(row["meal"]),
                country=clean_value(row["country"]),
                market_segment=clean_value(row["market_segment"]),
                distribution_channel=clean_value(row["distribution_channel"]),
                is_repeated_guest=clean_value(row["is_repeated_guest"], "int"),
                previous_cancellations=clean_value(row["previous_cancellations"], "int"),
                previous_bookings_not_canceled=clean_value(row["previous_bookings_not_canceled"], "int"),
                reserved_room_type=clean_value(row["reserved_room_type"]),
                assigned_room_type=clean_value(row["assigned_room_type"]),
                booking_changes=clean_value(row["booking_changes"], "int"),
                deposit_type=clean_value(row["deposit_type"]),
                agent=clean_value(row["agent"]),
                company=clean_value(row["company"]),
                days_in_waiting_list=clean_value(row["days_in_waiting_list"], "int"),
                customer_type=clean_value(row["customer_type"]),
                adr=clean_value(row["adr"], "float"),
                required_car_parking_spaces=clean_value(row["required_car_parking_spaces"], "int"),
                total_of_special_requests=clean_value(row["total_of_special_requests"], "int"),
                reservation_status=clean_value(row["reservation_status"]),
                reservation_status_date=clean_value(row["reservation_status_date"]),
            )
            bookings.append(booking)

            # Bulk insert in batches of 5000 for performance
            if len(bookings) >= 5000:
                db.bulk_save_objects(bookings)
                db.commit()
                print(f"  Imported {i + 1} records...")
                bookings = []

    # Insert remaining records
    if bookings:
        db.bulk_save_objects(bookings)
        db.commit()

    total = db.query(Booking).count()
    print(f"Import complete. Total bookings in database: {total}")
    db.close()


if __name__ == "__main__":
    import_csv()
