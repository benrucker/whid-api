from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Message(BaseModel):
    msg_id: int
    timestamp: str
    content: str
    author: int
    replying_to: Optional[int]
    edited: bool
    edited_timestamp: Optional[str]
    deleted: bool


@app.put("/message/{msg_id}")
def add_message(msg_id: int, message: Message):
    return {"msg_id": msg_id, "message": message}


@app.get("/message/{msg_id}")
def read_message(msg_id: int):
    return {"item_id": msg_id}


@app.post("/message/{msg_id}")
def update_message(msg_id: int, message: dict):
    return message
