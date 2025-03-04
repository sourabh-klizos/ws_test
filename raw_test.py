import asyncio
import random
import string
import websockets
from pymongo import MongoClient
import httpx
import json
from datetime import datetime

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI
db = client["chat_app"]  # Replace with your database name
users_collection = db["users"]  # Replace with your collection name

# Helper function to generate random strings
def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

class UserBehavior:
    def __init__(self):
        self.all_users = []  # This will store the user_id and token of all the created users
        self.active_connections = 0  # Track the number of active WebSocket connections

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

        # Make the POST request for signup
        response = await self.make_http_request("POST", "http://localhost:8000/api/v1/auth/signup", json=signup_payload)
        if response.status_code == 201:
            print(f"User {email} signed up successfully.")
        else:
            print(f"Failed to sign up user {email}. Response: {response.text}")

        # Login payload
        login_payload = {
            "email": email,
            "password": password
        }

        # Send POST request to login
        response = await self.make_http_request("POST", "http://localhost:8000/api/v1/auth/login", json=login_payload)
        if response.status_code == 200:
            # Capture the access_token, refresh_token, and user_id from the login response
            token = response.json().get("access_token")
            user_id = response.json().get("user_id")
            print(f"User {email} logged in successfully with user_id: {user_id} and token.")

            # Store the user_id and token in the all_users list
            self.all_users.append({"user_id": user_id, "token": token})
            print(f"Current users: {self.all_users}")  # Debug statement
        else:
            print(f"Failed to log in user {email}. Response: {response.text}")

    async def chat_with_random_user(self):
        # Ensure there are at least two users for chat
        if len(self.all_users) >= 2:
            await self.chat_with_random_user_async()
        else:
            print("Not enough users available for chat. Waiting for more users...")

    async def chat_with_random_user_async(self):
        # Randomly pick a user from the list of created users (but not the current one)
        selected_user = random.choice(self.all_users)
        selected_user_id = selected_user['user_id']

        print(f"Total users ==================== {self.all_users}. Response: {selected_user_id}")

        # Get the current user's token
        current_user = random.choice([u for u in self.all_users if u['user_id'] != selected_user_id])
        token = current_user['token']
        current_id = current_user['user_id']

        # WebSocket URL using the selected user's ID and current user's token
        websocket_url = f"ws://localhost:8000/ws/{selected_user_id}/?token={token}"

        print(f"WebSocket URL ==================== {websocket_url}.")

        # Open a WebSocket connection and send a message using the websockets library
        await self.send_message_via_websocket(websocket_url, current_id,selected_user_id)

    async def send_message_via_websocket(self, websocket_url,current_id ,selected_user_id):
        # Open a WebSocket connection using the websockets library
        async with websockets.connect(websocket_url) as ws:
            self.active_connections += 1
            print(f"Active WebSocket connections: {self.active_connections}")

        # async with websockets.connect("ws://localhost:8000/ws/status/?token={token}") as ws2:
        #     self.active_connections += 1

            try:
                while True:
                    message = "Hello! This is a message from WebSocket load test."

                    message = {
                            "text": "Hello! This is a message from WebSocket load test.",
                            "sender_id": current_id,
                            "receiver_id": selected_user_id,
                            "created_at": datetime.now(),

                    }
                    message = json.dumps(message, default=str)
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
                self.active_connections -= 1
                print(f"Active WebSocket connections after closure: {self.active_connections}")

    async def make_http_request(self, method, url, **kwargs):
        # This is a placeholder function. Implement HTTP request logic here.
        # You can use a library like `httpx` or `aiohttp` for async HTTP requests.
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, **kwargs)
            return response

    async def on_start(self):
        """This method is called when a simulated user starts."""
        await asyncio.sleep(random.uniform(1, 3))  # Sleep to simulate real-world delay

    def get_random_user_from_mongodb(self):
        """Query a random user from MongoDB."""
        count = users_collection.count_documents({})
        if count == 0:
            print("No users found in the database.")
            return None

        random_index = random.randint(0, count - 1)
        random_user = users_collection.find().skip(random_index).limit(1).next()
        return random_user

# Run the load test
async def main():
    user_behavior = UserBehavior()
    await user_behavior.on_start()

    # Simulate signup and login for multiple users
    await asyncio.gather(*[user_behavior.signup_and_login() for _ in range(10)])

    # Simulate chat between random users
    await asyncio.gather(*[user_behavior.chat_with_random_user() for _ in range(100)])

    # Keep the script running to maintain WebSocket connections
    while True:
        await asyncio.sleep(5)  # Keep the main function alive

# Run the main function
asyncio.run(main())
