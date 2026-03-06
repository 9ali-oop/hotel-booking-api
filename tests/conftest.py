"""
Test configuration and fixtures.

Uses a true in-memory SQLite database for tests so that:
  - Tests are fast (no disk I/O)
  - Tests are isolated (fresh database each run)
  - No interference with the real database
  - No file cleanup issues on Windows
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Booking

# True in-memory SQLite — no file created, no cleanup needed.
# StaticPool ensures all sessions share the same connection so
# they all see the same in-memory database during the test run.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Dependency override that provides the test database session."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the database dependency for all tests
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables once before all tests, clean up after."""
    Base.metadata.create_all(bind=test_engine)

    # Insert sample booking data for testing
    db = TestSessionLocal()
    sample_bookings = [
        Booking(
            booking_id=1,
            hotel="Resort Hotel",
            is_canceled=0,
            lead_time=342,
            arrival_date_year=2015,
            arrival_date_month="July",
            arrival_date_week_number=27,
            arrival_date_day_of_month=1,
            stays_in_weekend_nights=0,
            stays_in_week_nights=0,
            adults=2,
            children=0,
            babies=0,
            meal="BB",
            country="PRT",
            market_segment="Direct",
            distribution_channel="Direct",
            is_repeated_guest=0,
            previous_cancellations=0,
            previous_bookings_not_canceled=0,
            reserved_room_type="C",
            assigned_room_type="C",
            booking_changes=3,
            deposit_type="No Deposit",
            agent=None,
            company=None,
            days_in_waiting_list=0,
            customer_type="Transient",
            adr=0,
            required_car_parking_spaces=0,
            total_of_special_requests=0,
            reservation_status="Check-Out",
            reservation_status_date="2015-07-01",
        ),
        Booking(
            booking_id=2,
            hotel="City Hotel",
            is_canceled=1,
            lead_time=50,
            arrival_date_year=2016,
            arrival_date_month="August",
            arrival_date_week_number=35,
            arrival_date_day_of_month=15,
            stays_in_weekend_nights=2,
            stays_in_week_nights=3,
            adults=2,
            children=1,
            babies=0,
            meal="HB",
            country="GBR",
            market_segment="Online TA",
            distribution_channel="TA/TO",
            is_repeated_guest=0,
            previous_cancellations=2,
            previous_bookings_not_canceled=0,
            reserved_room_type="A",
            assigned_room_type="A",
            booking_changes=0,
            deposit_type="No Deposit",
            agent="9",
            company=None,
            days_in_waiting_list=0,
            customer_type="Transient",
            adr=120.5,
            required_car_parking_spaces=0,
            total_of_special_requests=1,
            reservation_status="Canceled",
            reservation_status_date="2016-08-10",
        ),
        Booking(
            booking_id=3,
            hotel="Resort Hotel",
            is_canceled=0,
            lead_time=10,
            arrival_date_year=2016,
            arrival_date_month="August",
            arrival_date_week_number=35,
            arrival_date_day_of_month=20,
            stays_in_weekend_nights=1,
            stays_in_week_nights=2,
            adults=1,
            children=0,
            babies=0,
            meal="BB",
            country="ESP",
            market_segment="Corporate",
            distribution_channel="Corporate",
            is_repeated_guest=1,
            previous_cancellations=0,
            previous_bookings_not_canceled=5,
            reserved_room_type="A",
            assigned_room_type="A",
            booking_changes=2,
            deposit_type="Non Refund",
            agent="14",
            company="223",
            days_in_waiting_list=0,
            customer_type="Contract",
            adr=85.0,
            required_car_parking_spaces=1,
            total_of_special_requests=2,
            reservation_status="Check-Out",
            reservation_status_date="2016-08-23",
        ),
    ]
    db.bulk_save_objects(sample_bookings)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """Provide a test client for making HTTP requests."""
    return TestClient(app)
