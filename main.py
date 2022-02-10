from fastapi import FastAPI
from pydantic import BaseModel

tags = [
    {
        "name": "Messages",
        "description": "Store and update messages. Use `PUT` for adding and `PATCH` for updating."
    },
    {
        "name": "Channels",
        "description": "Manage records of channels."
    },
    {
        "name": "Reactions",
        "description": "Add and remove reactions."
    }
]


app = FastAPI(
    title="what have i done API",
    description="Yet another tool for Encouraging Extra-Effective Engagement!",
    openapi_tags=tags,
)


class Message(BaseModel):
    msg_id: int
    timestamp: str
    content: str
    author: int
    replying_to: int | None = None
    edited: bool = False
    edited_timestamp: int | None = None
    deleted: bool = False


class Reaction(BaseModel):
    user_id: int
    msg_id: int
    emoji: str


class Channel(BaseModel):
    chan_id: int
    name: str
    category: str
    thread: bool = False


class VoiceEvent(BaseModel):
    user_id: int
    type: str
    timestamp: str


@app.put("/message/{msg_id}", tags=['Messages'])
def add_message(msg_id: int, message: Message):
    return {"msg_id": msg_id, "message": message}


@app.get("/message/{msg_id}", tags=['Messages'])
def read_message(msg_id: int):
    return {"item_id": msg_id}


@app.patch("/message/{msg_id}", tags=['Messages'])
def update_message(msg_id: int, message: dict):
    # follow partial schema docs, search for 'patch'
    return message


@app.post("/reaction", tags=['Reactions'])
def add_reaction(reaction: Reaction):
    return {"msg_id": reaction.msg_id, "user_id": reaction.msg_id, "reaction": reaction.emoji}


@app.delete('/reaction', tags=['Reactions'])
def delete_reaction(reaction: Reaction):
    return {"msg_id": reaction.msg_id, "user_id": reaction.msg_id, "reaction": reaction.emoji}


@app.put("/channel/{chan_id}", tags=['Channels'])
def add_channel(chan_id: int, channel: Channel):
    return {"name": channel.name}


@app.get("/channel/{chan_id}", tags=['Channels'])
def read_channel(chan_id: int):
    return chan_id


@app.patch("/channel/{chan_id}", tags=['Channels'])
def update_channel(chan_id: int, channel: Channel):
    return {"name": channel.name}


@app.post("/voice_event", tags=["Events"])
def add_voice_event(event: VoiceEvent):
    return {"user": event.user_id, "action": event.type, "time": event.timestamp}


@app.put("/pin/{msg_id}", tags=["Messages"])
def pin_message(msg_id):
    return f'pinned {msg_id}'