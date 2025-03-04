from locust import HttpUser, task, between
import random
import string
import asyncio
import websockets
import json
from pymongo import MongoClient
from datetime import datetime


client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI
db = client["chat_app"]  # Replace with your database name
users_collection = db["users"]  # Replace with your collection name



def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def get_random_user_from_mongodb(self):
    """Query a random user from MongoDB."""
    random_user = users_collection.aggregate([{ "$sample": { "size": 1 } }]).next()
    return str(random_user['_id'])



class FastAPIUser(HttpUser):
    wait_time = between(1, 3)  # Simulate 1 to 3 seconds of wait time between tasks


    def __init__(self):
        self.current_user_id = None
        self.current_user_token = None
        self.email = None
        self.password = None
        self.selected_user = None

    async def signup_and_login(self):
        # Generate random username, email, and password for signup
        username = generate_random_string(8)
        email = f"{username}@test.com"
        password = generate_random_string(12)

        # Signup request payload
        signup_payload = {
            "username": username,
            "email": email,
            "password": password
        }


        response = await self.make_http_request("POST", "http://localhost:8000/api/v1/auth/signup", json=signup_payload)
        if response.status_code == 201:
            print(f"User {email} signed up successfully.")

            self.email = email
            self.password = email
        else:
            print(f"Failed to sign up user {email}. Response: {response.text}")

        # Login payload
        login_payload = {
            "email": email,
            "password": password
        }



        response = await self.make_http_request("POST", "http://localhost:8000/api/v1/auth/login", json=login_payload)
        if response.status_code == 200:
            # Capture the access_token, refresh_token, and user_id from the login response
            self.current_user_token = response.json().get("access_token")
            self.current_user_id  = response.json().get("user_id")


            print(f"User {email} logged in successfully with user_id: {self.current_user_id} and token.")

            # Store the user_id and token in the all_users list
            self.all_users.append({"user_id": self.current_user_token, "token": self.current_user_id})
            print(f"Current users: {self.all_users}")  # Debug statement
        else:
            print(f"Failed to log in user {email}. Response: {response.text}")


    async def chat_with_random_user_async(self):
        # Randomly pick a user from the list of created users (but not the current one)

        selected_user_id = get_random_user_from_mongodb()

        if selected_user_id == self.current_user_id:
            selected_user_id = get_random_user_from_mongodb()
        
        self.selected_user= selected_user_id

    

       
        websocket_url = f"ws://localhost:8000/ws/{selected_user_id}/?token={self.current_user_token}"

        print(f"WebSocket URL ==================== {websocket_url}.")

        # Open a WebSocket connection and send a message using the websockets library
        await self.send_message_via_websocket(websocket_url)



    
    async def send_message_via_websocket(self, websocket_url):
        # Open a WebSocket connection using the websockets library
        async with websockets.connect(websocket_url) as ws:

            print(f"Active WebSocket connections: ")

            try:
                while True:
                    message = {
                            "text": "message",
                            "sender_id": self.current_user_id,
                            "receiver_id": self.selected_user,
                            "created_at": datetime.now(),

                    }
                    message = json.loads(message)
                    await ws.send(message)
                    print(f"Sent message: {message}")

                    # Receive a message from the WebSocket server
                    response = await ws.recv()
                    print(f"Received message: {response}")

                    # Wait before sending the next message
                    await asyncio.sleep(random.uniform(1,2))  # Random delay between 1 to 5 seconds
            except websockets.ConnectionClosed:
                print(f"Connection closed: {websocket_url}")
            finally:

                print(f"Active WebSocket connections after closure:")

        