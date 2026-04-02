


def create_sample_hotel(client):
    
    hotel_res = client.post("/hotels/", params={
        "name": "Test Hotel", "address": "123 St",
        "city": "Surat", "state": "gujarat", "country": "india"
    })
    assert hotel_res.status_code == 200
    return hotel_res.json()["hotel_id"]



def test_create_room_invalid_inputs(client):
    
    hotel_res = client.post("/hotels/", params={
        "name": "Validation Hotel", "address": "123 St",
        "city": "Surat", "state": "gujarat", "country": "india"
    })
    
    
    assert hotel_res.status_code == 200
    hotel_id = hotel_res.json()["hotel_id"]

    #  negative total_rooms 
    response_neg_rooms = client.post(f"/rooms/{hotel_id}", params={
        "hotel_id": hotel_id,
        "room_type": "REGULAR",
        "price": 500,
        "total_rooms": -5,  # Invalid
    })
    
    
    assert response_neg_rooms.status_code == 422 

    #   negative price
    response_neg_price = client.post("/rooms/{hotel_id}", params={
        "hotel_id": hotel_id, 
        "room_type": "REGULAR",
        "price": -100,      # Invalid
        "total_rooms": 10,
    })
    
    assert response_neg_price.status_code == 422 

   
    
    response_bad_hotel = client.post("/rooms/{hotel_id}", params={
        "hotel_id": 99999,   
        "room_type": "REGULAR",
        "price": 500,
        "total_rooms": 10,
    })
    assert response_bad_hotel.status_code == 422
    
    
    
    
    
    
    #correct response

    correct_response = client.post(f"/rooms/{hotel_id}",params={
        "hotel_id": hotel_id,
        "room_type": "REGULAR",
        "price": 500,
        "total_rooms": 10,
    })
    
   
    assert correct_response.status_code == 201
    
    
    

    


def test_get_room_by_hotelid(client):
    hotel_id =  create_sample_hotel(client)


   
    create_response = client.post(f"/rooms/{hotel_id}", params={
        "hotel_id": hotel_id,
        "room_type": "REGULAR",
        "price": 500,
        "total_rooms": 10,
    })
    
    
  
    assert create_response.status_code == 201
    hotel_id = create_response.json()["hotel_id"]

    
    get_response = client.get(f"/rooms/{hotel_id}")

    assert get_response.status_code == 200
    
    # assert get_response.json()["hotel_id"] == hotel_id
   



    


def test_update_room(client):
    hotel_id = create_sample_hotel(client)
    
    
    create_response = client.post(f"/rooms/{hotel_id}", params={
        "hotel_id": hotel_id,
        "room_type": "REGULAR",
        "price": 500,
        "total_rooms": 10,
    })
    room_id = create_response.json()["room_id"]


    update_hotel = client.patch(f"/rooms/{hotel_id}/{room_id}", params={
        "hotel_id": hotel_id,
        "room_id": room_id,
        "price": 600, # Updated value
        "total_rooms": 10,
    })

    assert update_hotel.status_code == 200
 
    assert update_hotel.json()["price"] == 600


def test_delet_hotel(client):
    hotel_id = create_sample_hotel(client)
    create_response = client.post(f"/rooms/{hotel_id}", params={
        "hotel_id": hotel_id,
        "room_type": "REGULAR",
        "price": 500,
        "total_rooms": 10,
    })
    room_id = create_response.json()["room_id"]


    create_response = client.delete(f"/rooms/{hotel_id}/{room_id}")
    assert create_response.status_code==204
    
    
    #no hotel 
   
    x= 54
    no_hotel = client.delete(f"/rooms/{x}/{room_id}")
    assert no_hotel.status_code == 404
    
    #no room 
    no_room = client.delete(f"/rooms/{hotel_id}/{34}")
    assert no_room.status_code == 404
    
    
   
   
    
    