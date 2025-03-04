# import random
# import time
# import json
# import asyncio
# import websockets
# from locust import HttpUser, task, between
# from pymongo import MongoClient

# # MongoDB connection setup
# client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI
# db = client["chat_app"]  # Replace with your database name
# users_collection = db["users"]  # Replace with your collection name

# def get_random_user_from_mongodb():
#     """Query a random user from MongoDB."""
#     random_user = users_collection.aggregate([{ "$sample": { "size": 1 } }]).next()
#     return str(random_user['_id'])
# class ChatApiUser(HttpUser):
#     wait_time = between(1, 3)

#     def on_start(self):
#         """Sign up a new user and log them in to obtain the token and user_id."""
#         self.email = f"user{random.randint(1000, 9999)}@example.com"
#         self.username = f"user{random.randint(1000, 9999)}"
#         self.password = "password123"
#         self.signup()
#         self.login()

#     def signup(self):
#         """Simulate a user signing up by sending email, username, and password."""
#         signup_payload = {
#             "email": self.email,
#             "username": self.username,
#             "password": self.password
#         }

#         response = self.client.post("/api/v1/auth/signup", json=signup_payload)
#         if response.status_code == 201:
#             print(f"Successfully signed up user {self.username}")
#         else:
#             print(f"Failed to sign up user {self.username}")

#     def login(self):
#         """Simulate a user logging in to obtain an access token."""
#         login_payload = {
#             "email": self.email,
#             "password": self.password
#         }

#         response = self.client.post("/api/v1/auth/login", json=login_payload)
#         if response.status_code == 200:
#             login_data = response.json()
#             self.token = login_data["access_token"]
#             self.user_id = login_data["user_id"]
#             print(f"Successfully logged in, user ID: {self.user_id}, Token: {self.token}")
#         else:
#             print(f"Failed to log in with email {self.email}. Status code: {response.status_code}")
#             print(f"Response: {response.text}")

#     @task(1)
#     def get_chat_history(self):
#         """Simulate a user fetching chat history from the backend API."""
#         if not hasattr(self, 'token') or not hasattr(self, 'user_id'):
#             print("Error: Token or user_id not set, skipping get_chat_history task.")
#             return  # Skip task if token is not available
#         selected_user = get_random_user_from_mongodb()  # Get random user ID from MongoDB
#         headers = {
#             "Authorization": f"Bearer {self.token}",
#             "Content-Type": "application/json",
#         }
#         # Request to fetch the chat history
#         response = self.client.get(f"/api/v1/chat/history/{selected_user}", headers=headers)
#         if response.status_code == 200:
#             print(f"Chat history fetched for user {self.user_id} with selected user {selected_user}")
#         else:
#             print(f"Failed to fetch chat history for user {self.user_id} with selected user {selected_user}")


#     @task(2)
#     async def chat(self):
#         """Simulate a WebSocket message exchange."""
#         if not hasattr(self, 'token') or not hasattr(self, 'user_id'):
#             print("Error: Token or user_id not set, skipping WebSocket task.")
#             return  # Skip task if token is not available

#         selected_user = get_random_user_from_mongodb()  # Get random user from MongoDB
#         ws_url = f"ws://localhost:8000/ws/{selected_user}/?token={self.token}"  # Replace with your WebSocket URL
        
#         try:
#             async with websockets.connect(ws_url) as ws:
#                 print(f"Connected to WebSocket at {ws_url}")

#                 # Send a message
#                 message = {
#                     "text": "Hello!",
#                     "sender_id": self.user_id,
#                     "receiver_id": selected_user,
#                     "created_at": time.time(),
#                 }
#                 await ws.send(json.dumps(message))
#                 print(f"Sent message from user {self.user_id} to user {selected_user}")

#                 # Receive response (simulate waiting for a reply)
#                 response = await ws.recv()
#                 print(f"Received message: {response}")

#         except Exception as e:
#             print(f"Error connecting to WebSocket: {e}")





# class WebSocketChatUser(HttpUser):
#     wait_time = between(1, 2)  # Simulate a user wait time for WebSocket messages

#     @task(1)
#     async def chat(self):
#         """Simulate a WebSocket message exchange."""
#         if not hasattr(self, 'token') or not hasattr(self, 'user_id'):
#             print("Error: Token or user_id not set, skipping WebSocket task.")
#             return  # Skip task if token is not available

#         selected_user = get_random_user_from_mongodb()  # Get random user from MongoDB
#         ws_url = f"ws://localhost:8000/ws/{selected_user}/?token={self.token}"  # Replace with your WebSocket URL
        
#         try:
#             async with websockets.connect(ws_url) as ws:
#                 print(f"Connected to WebSocket at {ws_url}")

#                 # Send a message
#                 message = {
#                     "text": "Hello!",
#                     "sender_id": self.user_id,
#                     "receiver_id": selected_user,
#                     "created_at": time.time(),
#                 }
#                 await ws.send(json.dumps(message))
#                 print(f"Sent message from user {self.user_id} to user {selected_user}")

#                 # Receive response (simulate waiting for a reply)
#                 response = await ws.recv()
#                 print(f"Received message: {response}")

#         except Exception as e:
#             print(f"Error connecting to WebSocket: {e}")

















import random
import time
import json
import gevent
from locust import HttpUser, task, between
from pymongo import MongoClient
import websockets


# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI
db = client["chat_app"]  # Replace with your database name
users_collection = db["users"]  # Replace with your collection name

def get_random_user_from_mongodb():
    """Query a random user from MongoDB."""
    random_user = users_collection.aggregate([{ "$sample": { "size": 1 } }]).next()
    return str(random_user['_id'])

class ChatApiUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Sign up a new user and log them in to obtain the token and user_id."""
        self.email = f"user{random.randint(1000, 9999)}@example.com"
        self.username = f"user{random.randint(1000, 9999)}"
        self.password = "password123"
        self.signup()
        self.login()

    def signup(self):
        """Simulate a user signing up by sending email, username, and password."""
        signup_payload = {
            "email": self.email,
            "username": self.username,
            "password": self.password
        }

        response = self.client.post("/api/v1/auth/signup", json=signup_payload)
        if response.status_code == 201:
            print(f"Successfully signed up user {self.username}")
        else:
            print(f"Failed to sign up user {self.username}")

    def login(self):
        """Simulate a user logging in to obtain an access token."""
        login_payload = {
            "email": self.email,
            "password": self.password
        }

        response = self.client.post("/api/v1/auth/login", json=login_payload)
        if response.status_code == 200:
            login_data = response.json()
            self.token = login_data["access_token"]
            self.user_id = login_data["user_id"]
            print(f"Successfully logged in, user ID: {self.user_id}, Token: {self.token}")
        else:
            print(f"Failed to log in with email {self.email}. Status code: {response.status_code}")
            print(f"Response: {response.text}")

    @task(1)
    def get_chat_history(self):
        """Simulate a user fetching chat history from the backend API."""
        if not hasattr(self, 'token') or not hasattr(self, 'user_id'):
            print("Error: Token or user_id not set, skipping get_chat_history task.")
            return  # Skip task if token is not available
        selected_user = get_random_user_from_mongodb()  # Get random user ID from MongoDB
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        # Request to fetch the chat history
        response = self.client.get(f"/api/v1/chat/history/{selected_user}", headers=headers)
        if response.status_code == 200:
            print(f"Chat history fetched for user {self.user_id} with selected user {selected_user}")
        else:
            print(f"Failed to fetch chat history for user {self.user_id} with selected user {selected_user}")

    @task(2)
    def start_chat(self):
        """Ensure that async task is properly handled."""
        # Use gevent to spawn a greenlet for the async chat task
        gevent.spawn(self.chat)

    def chat(self):
        """Simulate a WebSocket message exchange."""
        if not hasattr(self, 'token') or not hasattr(self, 'user_id'):
            print("Error: Token or user_id not set, skipping WebSocket task.")
            return  # Skip task if token is not available

        selected_user = get_random_user_from_mongodb()  # Get random user from MongoDB
        print("-===============================================",selected_user)
        ws_url = f"ws://localhost:8000/ws/{selected_user}?token={self.token}"  # Replace with your WebSocket URL
        # print("-===============================================",ws_url)

        print(f"Connecting to WebSocket: {ws_url}")
        
        try:
            # Now no need for asyncio, directly use websockets connect here
            loop = gevent.spawn(self._chat, ws_url)  # Use gevent to run the task asynchronously
            loop.join()

        except Exception as e:
            print(f"Error connecting to WebSocket: {e}")

    def _chat(self, ws_url):
        """The actual WebSocket communication."""
        try:
            # Open WebSocket connection
            ws = websockets.connect(ws_url)
            print(f"Connected to WebSocket at {ws_url}")

            # Send a message
            message = {
                "text": "Hello!",
                "sender_id": self.user_id,
                "receiver_id": get_random_user_from_mongodb(),
                "created_at": time.time(),
            }
            ws.send(json.dumps(message))
            print(f"Sent message from user {self.user_id}")

            # Receive response (simulate waiting for a reply)
            response = ws.recv()
            print(f"Received message: {response}")

        except Exception as e:
            print(f"Error in WebSocket communication: {e}")
