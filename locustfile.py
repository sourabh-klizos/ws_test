import random
import string
import websockets
import asyncio
from pymongo import MongoClient
import httpx
from locust import HttpUser, task, between






# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI
db = client["chat_app"]  # Replace with your database name
users_collection = db["users"]  # Replace with your collection name

# Helper function to generate random strings
def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

class WebSocketUser(HttpUser):
    wait_time = between(1, 3)  # Simulate 1 to 3 seconds of wait time between tasks
    all_users = []  # This will store the user_id and token of all the created users

    def on_start(self):
        """This method is called when a simulated user starts."""
        self.client = httpx.AsyncClient()  # Use AsyncClient for HTTP requests
        self.user_data = None
        self.token = None
        self.user_id = None

    @task(3)  # Higher weight to ensure more signups
    async def signup_and_login(self):
        """Sign up a new user and log in."""
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
        response = await self.client.post("/api/v1/auth/signup", json=signup_payload)
        if response.status_code == 201:
            print(f"User {email} signed up successfully.")
        else:
            print(f"Failed to sign up user {email}. Response: {response.text}")
            return

        # Login payload
        login_payload = {
            "email": email,
            "password": password
        }

        # Send POST request to login
        response = await self.client.post("/api/v1/auth/login", json=login_payload)
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.user_id = response.json().get("user_id")
            print(f"User {email} logged in successfully with user_id: {self.user_id} and token.")
            WebSocketUser.all_users.append({"user_id": self.user_id, "token": self.token})
            print(f"Current users: {WebSocketUser.all_users}")
        else:
            print(f"Failed to log in user {email}. Response: {response.text}")

    @task(1)
    async def chat_with_random_user(self):
        """Initiate a chat with a random user."""
        # Ensure there are at least two users for chat
        if len(WebSocketUser.all_users) >= 2:
            await self.chat_with_random_user_async()
        else:
            print("Not enough users available for chat. Waiting for more users...")

    async def chat_with_random_user_async(self):
        """Async function to handle WebSocket communication with a random user."""
        try:
            # Randomly pick a different user (the one receiving the message)
            selected_user = random.choice([u for u in WebSocketUser.all_users if u['user_id'] != self.user_id])
            websocket_url = f"ws://localhost:8000/ws/{selected_user['user_id']}/?token={self.token}"
            await self.send_message_via_websocket(websocket_url)
        except Exception as e:
            print(f"Error in chat_with_random_user_async: {e}")

    async def send_message_via_websocket(self, websocket_url):
        """Send a message via WebSocket."""
        try:
            # Open a WebSocket connection using the websockets library
            async with websockets.connect(websocket_url) as ws:
                message = f"Hello! This is a message from user {self.user_id}."
                await ws.send(message)
                print(f"Sent message: {message}")

                # Receive a message from the WebSocket server
                response = await ws.recv()
                print(f"Received message: {response}")
        except Exception as e:
            print(f"Error in send_message_via_websocket: {e}")

    def get_random_user_from_mongodb(self):
        """Query a random user from MongoDB."""
        random_user = users_collection.aggregate([{ "$sample": { "size": 1 } }]).next()
        return random_user
