import websockets
import asyncio

async def test_ws():
    ws_url = "ws://localhost:8000/ws/67bed0893db3a187d28a729a?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjdjNzAzOTE0MWNmNTY0MzFkODQ0NWRhIiwiZXhwIjoxNzQxMDk3NjI1LCJpYXQiOjE3NDEwOTU4MjUsImp0aSI6IjQwOWRiODExLTY3MjUtNGFkNi05MjU3LWM3MDZmYmYyNmNiYyIsInR5cCI6ImFjY2Vzc190b2tlbiJ9.6VENHO1SJNkNGxwWDVA55g-LJnz71aTtv05eOf4ZTZs"
    try:
        async with websockets.connect(ws_url) as ws:
            print("WebSocket connected")
            await ws.send("Hello WebSocket!")
            response = await ws.recv()
            print(f"Received: {response}")
    except Exception as e:
        print(f"Error connecting to WebSocket: {e}")

asyncio.run(test_ws())