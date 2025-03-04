import random
import time
import json
import requests
import websockets
import asyncio
from pymongo import MongoClient


# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI
db = client["chat_app"]  # Replace with your database name
users_collection = db["users"]  # Replace with your collection name

def get_random_user_from_mongodb():
    """Query a random user from MongoDB."""
    random_user = users_collection.aggregate([{ "$sample": { "size": 1 } }]).next()
    return str(random_user['_id'])

def generate_user_credentials():
    """Generate dynamic user email, username, and password."""
    email = f"user{random.randint(1000, 9999)}@example.com"
    username = f"user{random.randint(1000, 9999)}"
    password = f"password{random.randint(1000, 9999)}"  # Adding randomness to the password as well
    return email, username, password

# Signup function
def signup(email, username, password):
    """Simulate a user signing up by sending email, username, and password."""
    signup_payload = {
        "email": email,
        "username": username,
        "password": password
    }

    response = requests.post("http://localhost:8000/api/v1/auth/signup", json=signup_payload)
    if response.status_code == 201:
        print(f"Successfully signed up user {username}")
    else:
        print(f"Failed to sign up user {username}")
        print(f"Error: {response.text}")

# Login function
def login(email, password):
    """Simulate a user logging in to obtain an access token."""
    login_payload = {
        "email": email,
        "password": password
    }

    response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_payload)
    if response.status_code == 200:
        login_data = response.json()
        print(f"Successfully logged in, user ID: {login_data['user_id']}, Token: {login_data['access_token']}")
        return login_data['access_token'], login_data['user_id']
    else:
        print(f"Failed to log in with email {email}. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None, None

# WebSocket chat function
async def websocket_chat(token, user_id):
    """Simulate a WebSocket message exchange."""
    selected_user = get_random_user_from_mongodb()  # Get random user from MongoDB
    ws_url = f"ws://localhost:8000/ws/{selected_user}/?token={token}"  # WebSocket URL
    
    print(f"Connecting to WebSocket: {ws_url}")
    
    try:
        # Await websockets.connect to get the actual connection object
        async with websockets.connect(ws_url) as ws:
            print(f"Connected to WebSocket at {ws_url}")

            # Send a message
            message = {
                "text": "Hello!",
                "sender_id": user_id,
                "receiver_id": selected_user,
                "created_at": time.time(),
            }
            await ws.send(json.dumps(message))  # Send message to WebSocket
            print(f"Sent message from user {user_id}")

            # Receive response (simulate waiting for a reply)
            response = await ws.recv()
            print(f"Received message: {response}")

    except Exception as e:
        print(f"Error in WebSocket communication: {e}")

# Main function to test the signup, login, and WebSocket
def main():
    # 1. Generate dynamic user credentials
    email, username, password = generate_user_credentials()
    
    # 2. Simulate signup
    signup(email, username, password)
    
    # 3. Simulate login and get token and user_id
    token, user_id = login(email, password)
    
    if token and user_id:
        # 4. WebSocket chat communication
        asyncio.run(websocket_chat(token, user_id))

if __name__ == "__main__":
    main()
