import requests

BASE_URL = "http://localhost:8000"

# CREATE Account
response = requests.post(
    f"{BASE_URL}/accounts/",
    json={
        "user_id": 1,
        "provider": "youtube",
        "post_enabled": True,
        "config": {
            "channel_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
            "access_token": "ya29.a0AfH6SMBx..."
        }
    }
)
print(response.json())

# GET User's Accounts
response = requests.get(f"{BASE_URL}/accounts/user/1")
print(response.json())

# UPDATE Account
response = requests.patch(
    f"{BASE_URL}/accounts/1",
    json={"post_enabled": False}
)
print(response.json())

# DELETE Account
response = requests.delete(f"{BASE_URL}/accounts/1")
print(response.json())
