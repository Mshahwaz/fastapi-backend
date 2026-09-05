from fastapi.testclient import TestClient #Test client use for Fastapi endpoints testing specifically
# from logging_demo import app
from main import app
client=TestClient(app)

# def test_logging_demo():

#     response=client.get("/logging-demo")

#     assert response.status_code == 200
#     assert response.json() == {
#         "message" : "Logging demo completed"
#     }

def test_register_user():
    response = client.post(
        "/register",
        json={
            "name":"Mohd Shahwaz",
            "age":25,
            "username":"shani",
            "password":"shani@123"
        }
    )

    assert response.status_code == 201
    data=response.json()

    assert data["name"] == "Mohd Shahwaz"
    assert data["age"] == 25
    assert data["username"] == "shani"
    
    assert "id" in data
    assert "password" not in data

def test_register_age_parameter(): #Acc to business logic
    response = client.post(
        "/register",
        json={
            "name":"Mohd Shahwaz",
            "age":17,
            "username":"shani",
            "password":"shani@123"    
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "User  must be al least 18 years"
    )

def test_register_invalid_age(): #Pydantic Validation 

    response = client.post(
        "/register",
        json={
            "name":"Mohd Shahwaz",
            "age":170,
            "username":"shani",
            "password":"shani@123" 
        }
    )

    assert response.status_code == 422

def test_get_users():

    response=client.get("/users")

    assert response.status_code == 200

    assert isinstance(response.json(),list)

def test_get_user():
    id=1
    response=client.get(
        f"/users/{id}"
    )
    response.status_code == 200
    data=response.json()

    assert data["id"] == 1
    assert "name" in data
    assert "age" in data
    assert "username" in data

def test_get_user_not_found():
    user_id=99
    response = client.get(
        f"/users/{user_id}"
    )

    assert response.status_code == 404
    data=response.json()
    assert data["detail"] == (
        f"User with id {user_id} not found"
    )

def test_update_user():
    user_id=2
    payload ={
        "name": "Akram",
        "age":45,
        "username":"akram",
        "password":"akram@123"
    }
    response=client.put(
        f"/users/{user_id}",
        json=payload
    )

    assert response.status_code == 200

    data=response.json()

    assert data["id"] == user_id
    assert data["name"] == "Akram"
    assert data["age"] == 45
    assert data["username"] == "akram"
    assert "password" not in data

def test_update_user_not_found():
    user_id=99
    payload ={
        "name": "Akram",
        "age":45,
        "username":"akram",
        "password":"akram@123"
    }
    response=client.put(
        f"/users/{user_id}",
        json=payload
    )

    assert response.status_code == 404
    data=response.json()
    assert data["detail"] == (
        f"User not found with id {user_id}"
    )
    
def test_update_invalid_age(): #Pydantic Validation
    user_id=99
    payload ={
        "name": "Akram",
        "age":200,
        "username":"akram",
        "password":"akram@123"
    }
    response=client.put(
        f"/users/{user_id}",
        json=payload
    )    
    
    assert response.status_code == 422 

def test_update_valid_age_range(): #Business logic Validation
    user_id=99
    payload ={
        "name": "Akram",
        "age":17,
        "username":"akram",
        "password":"akram@123"
    }
    response=client.put(
        f"/users/{user_id}",
        json=payload
    )
    assert response.status_code == 400
    data=response.json()
    assert data["detail"] == (
        "User must be al least 18 years"
    )

def test_patch_name_only(): #Age should not be changed
    user_id=5
    before=client.get(
        f"/users/{user_id}"
    )
    payload_name_only={
        "name":"RAHMAN"
    }
    after=client.patch(
        f"/users/{user_id}",
        json=payload_name_only
    )
    data_after=after.json()
    data_before=before.json()

    assert after.status_code == 200
    assert data_after["id"] == user_id
    assert data_after["name"] == "RAHMAN"
    assert data_before["age"] == data_after["age"]
    assert "username" in data_after
    assert "password" not in data_after

def test_patch_age_only(): #Name should not be changed
    user_id=5
    before=client.get(
        f"/users/{user_id}"
    )
    payload_age_only={
        "age":26
    }
    after=client.patch(
        f"/users/{user_id}",
        json=payload_age_only
    )
    data_after=after.json()
    data_before=before.json()

    assert after.status_code == 200
    assert data_after["id"] == user_id
    assert data_after["age"] == 26
    assert data_before["name"] == data_after["name"]
    assert "username" in data_after
    assert "password" not in data_after

# def test_patch_user():
#     user_id=4
#     payload_name_only={
#         "name":"RAHMAN"
#     }
#     payload_age_only={
#         "age":56
#     }
#     payload_both={
#         "name":"RAJMAN",
#         "age":63
#     }
#     response = client.patch(
#         f"/users/{user_id}",
#         json=payload_both
#     )

#     response.status_code == 200

#     data=response.json()
#     assert data["id"] == user_id
#     assert data["name"] == "RAJMAN"
#     assert "age" in data
#     assert "username" in data
#     assert "password" not in data

def test_patch_user_not_found():
    user_id=99
    payload={
        "name":"SHAN",
        "age":23
    }
    response=client.patch(
        f"/users/{user_id}",
        json=payload
    )
    assert response.status_code == 404
    data=response.json()
    assert data["detail"] == (
        f"User not found with id {user_id}"
    )
    
def test_patch_invalid_age(): #Pydantic Validation
    user_id=10
    payload={
        "name":"SHAN",
        "age":200
    }
    response=client.patch(
        f"/users/{user_id}",
        json=payload
    )   
    assert response.status_code == 422

def test_patch_valid_age_range(): #Business logic Validation
    user_id=12
    payload={
        "name":"SHAN",
        "age":12
    }
    response=client.patch(
        f"/users/{user_id}",
        json=payload
    )
    assert response.status_code == 400
    data=response.json()
    assert data["detail"] == (
        "User must be al least 18 years"
    )