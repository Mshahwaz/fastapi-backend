from fastapi.testclient import TestClient #Test client use for Fastapi endpoints testing specifically
# from logging_demo import app
from main import app
client=TestClient(app)
from config import SECRET_KEY, ALGORITHM
from jose import jwt

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

def test_patch_user_both():
    user_id=4
    payload_both={
        "name":"RAJMAN",
        "age":63
    }
    response = client.patch(
        f"/users/{user_id}",
        json=payload_both
    )

    response.status_code == 200

    data=response.json()
    assert data["id"] == user_id
    assert data["name"] == "RAJMAN"
    assert "age" in data
    assert "username" in data
    assert "password" not in data

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

def test_successfull_login():
    payload={
        "username":"shani",
        "password":"shani@123"
    }
    response=client.post(
        "/login",
        json=payload
    )
    data=response.json()
    assert response.status_code == 200
    assert data["message"] == "Login Successfull"
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    
def test_login_invalid_username():
    payload={
        "username":"doesnotexist",
        "password":"shani@123"
    }
    response=client.post(
        "/login",
        json=payload
    )
    data=response.json()
    assert response.status_code == 401
    assert data["detail"] == (
        "Invalid Username or password"
    )

def test_login_invalid_password():
    payload={
        "username":"shani",
        "password":"wrong-pass"
    }
    response=client.post(
        "/login",
        json=payload
    )
    data=response.json()
    assert response.status_code == 401
    assert data["detail"] == (
        "Invalid Username or password"
    )

def test_protected_endpoint_successfull():

    login_response=client.post(
        "/login",
        json={
            "username":"shani",
            "password":"shani@123"
        }
    )
    assert login_response.status_code == 200

    token=login_response.json()["access_token"]
    protected_response=client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    data=protected_response.json()
    assert protected_response.status_code == 200
    assert data["username"] == "shani"
    assert data["message"] == "You are authenticated"
    assert "user_id" in data
    assert "name" in data
    assert "role" in data

def test_protected_without_token():
    response=client.get("/protected")

    assert response.status_code == 401

def test_protected_with_invalid_token():
    response=client.get(
        "/protected",
        headers={
            "Authorization": "Bearer This is not valid token"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid or Expired token"
    )

def test_protected_with_valid_token_without_username():

    token=jwt.encode(
        {
            "role":"user"
        },
        SECRET_KEY,
        ALGORITHM
    )

    response=client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid Token"
    )


def test_protected_with_valid_token_invalid_username():
    token=jwt.encode(
        {   
            "sub":"AKRAMA",
            "role":"user"
        },
        SECRET_KEY,
        ALGORITHM
    )

    response=client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "User not found"
    )
    

def test_admin_dashboard_with_admin_user():

    login_data=client.post(
        "/login",
        json={
            "username": "admin",
            "password" : "admin"
        }
    )
    
    assert login_data.status_code == 200

    token=login_data.json()["access_token"]

    admin_response=client.get(
        "/admin/dashboard",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert admin_response.status_code == 200
    assert admin_response.json()["message"] == (
        " Welcome to Admin Dashboard "
    )
    assert "user" in admin_response.json()

def test_admin_dashboard_with_normal_user():

    login_data=client.post(
        "/login",
        json={
            "username": "shani",
            "password" : "shani@123"
        }
    )
    
    assert login_data.status_code == 200

    token=login_data.json()["access_token"]

    admin_response=client.get(
        "/admin/dashboard",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert admin_response.status_code == 403
    assert admin_response.json()["detail"] == (
        "Admin Access required"
    )

def test_admin_dashboard_with_valid_token_invalid_username():
    token=jwt.encode(
        {   
            "sub":"AKRAMA",
            "role":"user"
        },
        SECRET_KEY,
        ALGORITHM
    )
    response=client.get("/admin/dashboard",
    headers={
        "Authorization": f"Bearer {token}"
    }    
    )
    assert response.status_code == 401
    assert response.json()["detail"] == (
        "User not found"
    )


def test_admin_dashboard_valid_token_without_username():

    token=jwt.encode(
        {
            "role":"user"
        },
        SECRET_KEY,
        ALGORITHM
    )

    response=client.get(
        "/admin/dashboard",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid Token"
    )

def test_admin_dashboard_without_token():
    response=client.get("/admin/dashboard")

    assert response.status_code == 401

def test_delete_existuser_with_admin_user():
    login_data=client.post(
    "/login",
    json={
        "username": "admin",
        "password" : "admin"
    }
    )

    assert login_data.status_code == 200

    token=login_data.json()["access_token"]
    
    user_id=5
    delete_response=client.delete(
        f"/users/{user_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert delete_response.status_code == 200 

    assert delete_response.json()["message"] == (
        f"User with id {user_id} has been removed successfully"
    )

def test_delete_with_normal_user():
    login_data=client.post(
    "/login",
    json={
        "username": "shani",
        "password" : "shani@123"
    }
    )

    assert login_data.status_code == 200

    token=login_data.json()["access_token"]
    
    user_id=18
    delete_response=client.delete(
        f"/users/{user_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert delete_response.status_code == 403 

    assert delete_response.json()["detail"] == (
        "Admin Access required"
    )

def test_delete__nonexistant_user_with_admin_user():
    login_data=client.post(
    "/login",
    json={
        "username": "admin",
        "password" : "admin"
    }
    )

    assert login_data.status_code == 200

    token=login_data.json()["access_token"]
    
    user_id=999
    delete_response=client.delete(
        f"/users/{user_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert delete_response.status_code == 404 

    assert delete_response.json()["detail"] == (
        f"User not found with id {user_id}"
    )
