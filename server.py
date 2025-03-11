import asyncio
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from threading import Thread
import uvicorn

app = FastAPI()
response_websocket = None

output_event_listeners = []
RETRY_DELAY = 5
audio_queue = asyncio.Queue()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def run_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=run_loop, daemon=True).start()

@app.websocket("/audio-response")
async def websocket_audio_response(websocket: WebSocket):
    """Handles WebSocket connections for sending audio responses back to client."""
    global response_websocket
    await websocket.accept()
    print("audio-response WebSocket connection established")
    response_websocket = websocket
    try:
        while True:
            audio_bytes = await audio_queue.get()
            await response_websocket.send_bytes(audio_bytes)
    except WebSocketDisconnect:
        response_websocket = None
        print("audio-response WebSocket disconnected. Attempting to reconnect...")
        await asyncio.sleep(RETRY_DELAY)
        await websocket_audio_response(websocket)




async def add_audio_to_queue(audio_data: bytes):
    await audio_queue.put(audio_data)

def send_audio_to_client(audio_data: bytes):
    asyncio.run_coroutine_threadsafe(add_audio_to_queue(audio_data), loop)
        


def send_output(output):
    for subscriber in output_event_listeners:
        subscriber(output)

def add_output_event_listener(function):
    output_event_listeners.append(function)

def run_websocket_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)

def start():
    server_thread = Thread(target=run_websocket_server)
    server_thread.start()

if __name__ == "__main__":
    run_websocket_server()
