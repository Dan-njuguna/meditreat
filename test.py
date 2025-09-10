import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://localhost:8002/ws/chat"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "user_id": "dd32681c-ef94-4b67-8227-af00253fa03f",
            "chat_id": "12ec5248-225f-407f-92c1-dbd619fabc6b",
            "message": "Hello",
            "llm": "openai"
        }))
        while True:
            msg = await websocket.recv()
            print("Received:", msg)
            if msg == "[DONE]":
                break

asyncio.run(test_ws())