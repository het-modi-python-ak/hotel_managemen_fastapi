import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
from unittest.mock import MagicMock
from app.main import app
from app.database.database import get_db
from app.core.dependencies import get_current_user

client = TestClient(app)


@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_redis(mocker):
    
    return mocker.patch("app.core.redis_client.redis_client")

@pytest.fixture
def mock_user():
    return MagicMock(id=1, email="test@user.com")

@pytest.fixture(autouse=True)
def setup_dependencies(mock_db, mock_user):
    
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.clear()



def test_create_booking_success(mock_db, mock_redis):
    # 1. Setup Mock Room
    mock_room = MagicMock(room_id=1, hotel_id=1, room_type="REGULAR", total_rooms=10, price=100)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_room
    
    # 2. Setup Availability (0 booked, 0 locked)
    mock_db.query.return_value.join.return_value.filter.return_value.scalar.return_value = 0
    mock_redis.get.return_value = None 

    payload = {
        "hotel_id": 1,
        "check_in": str(date.today() + timedelta(days=1)),
        "check_out": str(date.today() + timedelta(days=2)),
        "no_of_people": 2,
        "rooms": [{"room_type": "REGULAR", "quantity": 1}]
    }
    
    response = client.post("/bookings/", json=payload)
    
    assert response.status_code == 200
    # assert "booking_id" in response.json()
    # assert "Rooms locked" in response.json()["message"]

def test_create_booking_past_date():
    response = client.post("/bookings/", json={
        "hotel_id": 1,
        "check_in": str(date.today() - timedelta(days=1)),
        "check_out": str(date.today() + timedelta(days=1)),
        "no_of_people": 1,
        "rooms": [{"room_type": "deluxe", "quantity": 1}]
    })
    assert response.status_code == 400
    assert "past" in response.json()["detail"]

def test_confirm_booking_success(mock_db, mock_redis):
    # Mock finding the booking
    mock_booking = MagicMock(booking_id=1, user_id=1, status="pending")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_booking
    
    # Mock finding booking items
    mock_item = MagicMock(room_id=1, quantity=1)
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_item]
    
    mock_redis.exists.return_value = True

    response = client.put("/bookings/1")
    
    assert response.status_code == 200
    assert mock_booking.status == "confirmed"
    assert response.json()["message"] == "Booking confirmed"

def test_cancel_booking_success(mock_db, mock_redis):
    # Mock finding the booking
    mock_booking = MagicMock(booking_id=1, user_id=1, status="confirmed")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_booking
    
    # Mock items
    mock_db.query.return_value.filter.return_value.all.return_value = []

    response = client.delete("/bookings/1")
    
    assert response.status_code == 200
    assert mock_booking.status == "cancelled"
    assert response.json()["message"] == "Booking cancelled successfully"
