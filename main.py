import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from pydantic.networks import email_validator
from starlette.requests import Request

app = FastAPI(
    title="WebSocket Chat",
    description="A simple WebSocket chat application using FastAPI and WebSockets",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")


class BaseModel():
    created_at = datetime.datetime.now()
    updated_at = datetime.datetime.now()


class User(BaseModel):
    id: int
    first_name: str
    second_name: str
    email: email_validator
    is_active: bool
    is_superuser: bool
    # password: password_validator


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse('chat.html', {'request': request})


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

