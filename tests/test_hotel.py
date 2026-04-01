



def test_create_hotel(client):
    
    response = client.post(
        "/hotels/", 
        params={
            "name": "Test Hotel",
            "address": "123 Main St",
            "city": "Test City",
            "state": "gujarat", 
            "country": "india" 
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Hotel"
    assert data["owner_id"] == 1
    assert "hotel_id" in data # The created object should have an ID




def test_get_hotels_list(client):
    # First, create a hotel to ensure the list isn't empty
    client.post(
        "/hotels/", 
        params={
            "name": "Hotel A",
            "address": "456 Oak Ave",
            "city": "Another City",
            "state": "gujarat",
            "country": "india"
        }
    )
    
    response = client.get("/hotels/")
    print("the res is", response.json())
    assert response.status_code == 200
    assert len(response.json()) == 1 # Expecting one hotel in the list
    assert response.json()[0]["name"] == "Hotel A"



def test_get_single_hotel_by_id(client):
    # First, create a hotel and capture its ID
    create_response = client.post(
        "/hotels/", 
        params={
            "name": "Hotel B",
            "address": "789 Pine Ln",
            "city": "Third City",
            "state": "gujarat",
            "country": "india"
        }
    )
    assert create_response.status_code == 200
    hotel_id = create_response.json()["hotel_id"]
    print("hotel id is " , hotel_id)

    # Now request that specific hotel using its ID in the URL path
    # Assuming your endpoint is GET /hotels/{hotel_id}
    get_response = client.get(f"/hotels/{hotel_id}")
    
    assert get_response.status_code == 200
    hotel_data = get_response.json()
    assert hotel_data["name"] == "Hotel B"
    assert hotel_data["hotel_id"] == hotel_id
    



def test_get_non_existent_hotel(client):
    # Test that requesting an ID that doesn't exist returns a 404
    # Assuming your application handles non-existent resources with a 404
    response = client.get("/hotels/999") 
    assert response.status_code == 404
