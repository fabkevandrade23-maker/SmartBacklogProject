from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from routes import auth, tasks, ai, analytics
from websocket import websocket_endpoint

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(tasks.router, prefix="/tasks")
app.include_router(ai.router, prefix="/ai")
app.include_router(analytics.router, prefix="/analytics")

@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await websocket_endpoint(websocket)
