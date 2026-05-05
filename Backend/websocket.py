from fastapi import WebSocket

clients = []

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    while True:
        data = await websocket.receive_text()

        for client in clients:
            await client.send_text(data)