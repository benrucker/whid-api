from datetime import date
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


class User(BaseModel):
    user_id: int
    username: str
    nickname: str | None = None
    numbers: int


class Score(BaseModel):
    iteration: int
    user_id: int
    date_processed: date
    score: int


@app.get("/message/{msg_id}", tags=['Messages'])
def read_message(msg_id: int):
    return {"item_id": msg_id}


@app.put("/message/{msg_id}", tags=['Messages'])
def add_message(msg_id: int, message: Message):
    return {"msg_id": msg_id, "message": message}


@app.patch("/message/{msg_id}", tags=['Messages'])
def update_message(msg_id: int, message: Message):
    # follow partial schema docs, search for 'patch'
    return message


@app.put("/pin/{msg_id}", tags=["Messages"])
def pin_message(msg_id):
    return f'pinned {msg_id}'


@app.get("/user/{user_id}", tags=["Users"])
def get_user(user_id: int):
    return {"user_id": user_id}


@app.put("/user/{user_id}", tags=["Users"])
def add_user(user_id: int, data: User):
    return {"user_id": user_id, "data": data}


@app.patch("/user/{user_id}", tags=["Users"])
def update_user(user_id: int, data: User):
    # TODO partial
    return {"user_id": user_id, "data": data}


@app.get("/user/{user_id}/score", tags=["Users"])
def get_user_score(user_id: int):
    return {"user_id": user_id, "score": 500}


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
