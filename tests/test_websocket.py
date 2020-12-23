#!/usr/bin/env python

# WS client example

import asyncio
import websockets


async def hello():
    uri = "ws://localhost:5000"
    async with websockets.connect(uri) as websocket:
        name = input("What's your name? ")

        await websocket.send(name)
        print(f"> {name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

#def test_call_server():
print("calling...")
asyncio.get_event_loop().run_until_complete(hello())