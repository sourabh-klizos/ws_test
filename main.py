from locust import HttpUser, task, between
import random
import string
import asyncio
import websockets
import json
from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI
db = client["chat_app"]  # Replace with your database name
users_collection = db["users"]  # Replace with your collection name

class FastAPIUser(HttpUser):
    wait_time = between(1, 3)  # Simulate 1 to 3 seconds of wait time between tasks

    def on_start(self):
        """This method is called when a simulated user starts."""
        self.user_data = self.signup()
        if self.user_data:
            self.login()

    def random_string(self, length=8):
        """Generates a random string of a given length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def signup(self):
        """Handles the signup process."""
        random_username = self.random_string()
        user_payload = {
            "username": random_username,
            "email": f"{random_username}@example.com",
            "password": "testpassword123"
        }

        response = self.client.post("/api/v1/auth/signup", json=user_payload)

        if response.status_code == 201:
            print(f"User {random_username} signed up successfully.")
            return {
                "email": user_payload["email"],
                "password": user_payload["password"]
            }
        else:
            print(f"Signup failed: {response.text}")
            return None

    @task
    def login(self):
        """Logs the user in and retrieves the access token."""
        if self.user_data:
            login_payload = {
                "email": self.user_data["email"],
                "password": self.user_data["password"]
            }

            response = self.client.post("/api/v1/auth/login", json=login_payload)

            if response.status_code == 200:
                data = response.json()
                self.user_id = data["user_id"]
                self.access_token = data["access_token"]
                print(f"Login successful! User ID: {self.user_id}, Access Token: {self.access_token}")

                # Fetch a random user from the database for WebSocket connection
                selected_user = self.get_random_user_from_mongodb()
                print("user_________", selected_user)
                if selected_user:
                    # Properly construct the WebSocket URL with the selected user ID
                    self.ws_url = f"ws://localhost:8000/ws/{selected_user}?token={self.access_token}"
                    print(f"WebSocket URL: {self.ws_url}")
                else:
                    print("No other users found in the database for WebSocket connection.")
            else:
                print(f"Login failed: {response.text}")

    @task
    def websocket_chat(self):
        """Starts WebSocket chat with a random user."""
        if hasattr(self, "ws_url"):
            asyncio.run(self.ws_connect(self.ws_url))

    async def ws_connect(self, ws_url):
        """Connect to WebSocket server, send and receive messages."""
        try:
            print(f"Attempting to connect to WebSocket at: {ws_url}")
            async with websockets.connect(ws_url) as websocket:  # No timeout argument in connect
                print(f"WebSocket connected: {ws_url}")

                # Prepare message and send to WebSocket
                receiver_id = self.user_id
                random_message = self.random_message()
                msg_payload = f"{self.user_id}:{receiver_id}:{random_message}"

                await websocket.send(msg_payload)
                print(f"Sent: {msg_payload}")

                # Receive response from WebSocket
                response = await websocket.recv()
                print(f"Received: {response}")

        except asyncio.TimeoutError:
            print(f"Connection timed out while attempting to connect to {ws_url}.")
        except websockets.exceptions.InvalidURI:
            print(f"Invalid WebSocket URI: {ws_url}")
        except websockets.exceptions.WebSocketException as e:
            print(f"WebSocket error: {e}")

    def random_message(self):
        """Generates a random message for chat testing."""
        messages = [
            "Hey there!",
            "How's it going?",
            "What's up?",
            "Testing WebSockets!",
            "This is a random chat message.",
            "Hello from Locust!",
            "Sending random messages for load testing.",
            "FastAPI + WebSockets = Rocket",
            "Let's see how this chat handles load!",
            "Hello, world!"
        ]
        return random.choice(messages)

    def get_random_user_from_mongodb(self):
        """Fetch a random user from MongoDB."""
        try:
            random_user = users_collection.aggregate([{ "$sample": { "size": 1 } }]).next()
            # Returning the user_id as string for WebSocket URL
            print(random_user['_id'])
            return str(random_user['_id'])
        except Exception as e:
            print(f"Error fetching random user from MongoDB: {e}")
            return None
