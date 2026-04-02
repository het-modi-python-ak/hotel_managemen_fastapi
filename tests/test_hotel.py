



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
    assert data["owner_id"] == 2
    assert "hotel_id" in data 




def test_get_hotels_list(client):
    
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
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Hotel A"



def test_get_single_hotel_by_id(client):
   
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

    
    get_response = client.get(f"/hotels/{hotel_id}")
    
    assert get_response.status_code == 200
    hotel_data = get_response.json()
    assert hotel_data["name"] == "Hotel B"
    assert hotel_data["hotel_id"] == hotel_id
    



def test_get_non_existent_hotel(client):

    response = client.get("/hotels/999") 
    assert response.status_code == 404


def test_update_hotel(client):
    hotel_res = client.post(
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
    hotel_id = hotel_res.json()["hotel_id"]
    
    assert response.status_code == 200
    
    
    update_hotel = client.patch(f"/hotels/{hotel_id}", 
        json={
            "name": "Hotelopo",
            "address": "456 Oak Ave",
            "city": "Another City",
            "state": "gujarat",
            "country": "india"
        })
    
    assert update_hotel.status_code==200
    
    
    
    
    

def test_delete_hotel(client):
    hotel_res = client.post("/hotels/", params={
        "name": "Test Hotel", "address": "123 St",
        "city": "Surat", "state": "gujarat", "country": "india"
    })
    
    hotel_id = hotel_res.json()["hotel_id"]
    
    delete_hotel = client.delete(f"/hotels/{hotel_id}")
    assert delete_hotel.status_code == 200
    
    #entering wrong id
    x=5
    
    delete_hotel2 = client.delete(f"/hotels/{x}")
    assert delete_hotel2.status_code == 404
    
    
    
    
    