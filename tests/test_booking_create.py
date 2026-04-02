import pytest



@pytest.fixture
def setup_hotel_with_room(client):
    
    # Create Hotel
    hotel_res = client.post(
        "/hotels/", 
        params={
            "name": "Test Suite Hotel", 
            "address": "123 Main St", 
            "city": "Surat", 
            "state": "gujarat", 
            "country": "india"
        }
    )
    hotel_data = hotel_res.json()
    hotel_id = hotel_data["hotel_id"]

    # Create Room
    z =  client.post(
        f"/rooms/{hotel_id}", 
        params={
            "hotel_id": hotel_id, 
            "room_type": "DELUXE", 
            "price": 1000, 
            "total_rooms": 10
        }
    )
    
    return hotel_id

#  TEST CASES 

def test_get_all_my_bookings(client, setup_hotel_with_room):
    
    response = client.get("/booking/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_confirm_booking(client, setup_hotel_with_room): 
    # Create Booking 
    booking_res = client.post("/booking/", json={ 
        "hotel_id": setup_hotel_with_room, 
        "check_in": "2026-05-10", 
        "check_out": "2026-05-12", 
        "no_of_people": 2, 
        "rooms": [{"room_type": "DELUXE", "quantity": 1}] 
    }) 
    
    st  = booking_res.json()["status"]
    assert st == "pending"
    booking_id = booking_res.json()["booking_id"] 
    

    # Confirm Booking 
    confirm_res = client.patch(f"/booking/{booking_id}") 
    assert confirm_res.status_code == 200 
    assert "confirmed" in confirm_res.json()["message"].lower() 

    # Negative: no of people
    negative_people_book = client.post("/booking/", json={ 
        "hotel_id": setup_hotel_with_room, 
        "check_in": "2026-05-10", 
        "check_out": "2026-05-12", 
        "no_of_people": -5, 
        "rooms": [{"room_type": "DELUXE", "quantity": 1}] 
    }) 
    assert negative_people_book.status_code == 400

    
    
    #negative number of rooms
    
    negative_no_of_rooms = client.post(
        "/booking/",
        json={
            "hotel_id": setup_hotel_with_room, 
        "check_in": "2026-05-10", 
        "check_out": "2026-05-12", 
        "no_of_people": 5, 
        "rooms": [{"room_type": "DELUXE", "quantity": -5}] 
        }
        
        
        
    )
    
    
    
    
    
    
    assert negative_no_of_rooms.status_code==400
    
    
    #wrong category 
    
    wrong_category_room = client.post(
        "/booking",
        json={
            "hotel_id": setup_hotel_with_room, 
        "check_in": "2026-05-10", 
        "check_out": "2026-05-12", 
        "no_of_people": 5, 
        "rooms": [{"room_type": "BELUX", "quantity": 5}] 
            
        }
    )
    
    assert wrong_category_room.status_code == 404
    
    
    
    #neagtive number of people
    
    negative_no_of_people  = client.post(
        "/booking/",
        json={
           "hotel_id": setup_hotel_with_room,
            "check_in": "2026-05-10",
            "check_out": "2026-05-12",
            "no_of_people": -2,
            "rooms": [{"room_type": "DELUXE", "quantity": 9}]
        }
    )
    
    
    assert negative_no_of_people.status_code == 400
    
    
    
    #more number of rooms
    
    more_no_rooms = client.post(
        "/booking/",
        json={
             "hotel_id": setup_hotel_with_room,
            "check_in": "2026-05-10",
            "check_out": "2026-05-12",
            "no_of_people": 2,
            "rooms": [{"room_type": "DELUXE", "quantity": 19}]
        }
    )
    
    
    assert more_no_rooms.status_code == 409
    
    
    



def test_get_booking_details(client, setup_hotel_with_room):
    """Test retrieving specific booking details with room joins."""
    #  Create a booking first
    booking_res = client.post(
        "/booking/", 
        json={ 
            "hotel_id": setup_hotel_with_room,
            "check_in": "2026-06-01",
            "check_out": "2026-06-05",
            "no_of_people": 1,
            "rooms": [{"room_type": "DELUXE", "quantity": 2}]
        }
    )
    booking_id = booking_res.json()["booking_id"]

    #  Get Details
    response = client.get(f"/booking/{booking_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["booking_id"] == booking_id
    assert data["rooms_booked"][0]["room_type"] == "DELUXE"






def test_cancel_booking(client, setup_hotel_with_room):
   
    #  Create Booking
    booking_res = client.post(
        "/booking/", 
        json={ 
            "hotel_id": setup_hotel_with_room,
            "check_in": "2026-07-01",
            "check_out": "2026-07-02",
            "no_of_people": 1,
            "rooms": [{"room_type": "DELUXE", "quantity": 1}]
        }
    )
    booking_id = booking_res.json()["booking_id"]

    #  Cancel it
    response = client.delete(f"/booking/{booking_id}")
    assert response.status_code == 200
    assert "cancelled" in response.json()["message"].lower()

def test_booking_not_found_error(client):
    
    response = client.get("/booking/99999")
    assert response.status_code == 404
