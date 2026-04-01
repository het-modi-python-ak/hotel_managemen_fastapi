


def create_sample_hotel(client):
    
    hotel_res = client.post("/hotels/", params={
        "name": "Test Hotel", "address": "123 St",
        "city": "Surat", "state": "gujarat", "country": "india"
    })
    assert hotel_res.status_code == 200
    return hotel_res.json()["hotel_id"]



def test_create_room_invalid_inputs(client):
    #  Create a parent hotel
    hotel_res = client.post("/hotels/", params={
        "name": "Validation Hotel", "address": "123 St",
        "city": "Surat", "state": "gujarat", "country": "india"
    })
    
    #  hotel creation was successful to proceed
    assert hotel_res.status_code == 200
    hotel_id = hotel_res.json()["hotel_id"]

    # Test negative total_rooms - FastAPI uses 422 for validation errors
    response_neg_rooms = client.post("/rooms/", params={
        "hotel_id": hotel_id,
        "room_type": "REGULAR",
        "price": 500,
        "total_rooms": -5,  # Invalid
    })
    # Changed from 404 to 422
    assert response_neg_rooms.status_code == 422 

    #  Test negative price
    response_neg_price = client.post("/rooms/", params={
        "hotel_id": hotel_id, 
        "room_type": "REGULAR",
        "price": -100,      # Invalid
        "total_rooms": 10,
    })
    # Changed from 404 to 422
    assert response_neg_price.status_code == 422 

    # This might be 404 *if* your endpoint logic explicitly checks for existence 
    
    response_bad_hotel = client.post("/rooms/", params={
        "hotel_id": 99999,   
        "room_type": "REGULAR",
        "price": 500,
        "total_rooms": 10,
    })
    assert response_bad_hotel.status_code == 404 

    correct_response = client.post("/rooms",params={
        "hotel_id": hotel_id,
        "room_type": "REGULAR",
        "price": 500,
        "total_rooms": 10,
    })
    
   
    assert correct_response.status_code == 201

    


def test_get_room_by_hotelid(client):
    hotel_id =  create_sample_hotel(client)


   
    create_response = client.post("/rooms", params={
        "hotel_id": hotel_id,
        "room_type": "REGULAR",
        "price": 500,
        "total_rooms": 10,
    })
    
    
  
    assert create_response.status_code == 201
    hotel_id = create_response.json()["hotel_id"]

    
    get_response = client.get(f"/rooms/{hotel_id}")

    assert get_response.status_code == 200
    response_data = get_response.json()
    assert response_data["hotel_id"] == hotel_id
   
