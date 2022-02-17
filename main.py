from datetime import date
from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

tags = [
    {
        "name": "Messages",
        "description": "Store and update messages. Use `PUT` for adding and `PATCH` for updating."
    },
    {
        "name": "Users",
        "description": "Manage user metadata"
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
auth_scheme = HTTPBearer()
with open('.usertokens') as f:
    usertokens = f.readlines()


class Message(BaseModel):
    msg_id: int
    timestamp: str
    content: str
    # Attachments: relationship()
    author: int
    replying_to: int | None = None
    edited: bool = False
    edited_timestamp: int | None = None
    deleted: bool = False


class Attachments(BaseModel):
    msg_id: int
    url: str


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


def token(creds: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if creds.credentials not in usertokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        return creds


@app.get("/message/{msg_id}", tags=['Messages'])
def read_message(msg_id: int):
    return {"item_id": msg_id}


@app.put("/message/{msg_id}", tags=['Messages'])
def add_message(msg_id: int, message: Message, token: str = Depends(token)):
    return {"msg_id": msg_id, "message": message}


@app.patch("/message/{msg_id}", tags=['Messages'])
def update_message(msg_id: int, message: Message, token: str = Depends(token)):
    # follow partial schema docs, search for 'patch'
    return message


@app.put("/pin/{msg_id}", tags=["Messages"])
def pin_message(msg_id, token: str = Depends(token)):
    return f'pinned {msg_id}'


@app.get("/user/{user_id}", tags=["Users"])
def get_user(user_id: int):
    return {"user_id": user_id}


@app.put("/user/{user_id}", tags=["Users"])
def add_user(user_id: int, data: User, token: str = Depends(token)):
    return {"user_id": user_id, "data": data}


@app.patch("/user/{user_id}", tags=["Users"])
def update_user(user_id: int, data: User, token: str = Depends(token)):
    # TODO partial
    return {"user_id": user_id, "data": data}


@app.get("/user/{user_id}/score", tags=["Users"])
def get_user_score(user_id: int):
    return {"user_id": user_id, "score": 500}


@app.post("/reaction", tags=['Reactions'])
def add_reaction(reaction: Reaction, token: str = Depends(token)):
    return {"msg_id": reaction.msg_id, "user_id": reaction.msg_id, "reaction": reaction.emoji}


@app.delete('/reaction', tags=['Reactions'])
def delete_reaction(reaction: Reaction, token: str = Depends(token)):
    return {"msg_id": reaction.msg_id, "user_id": reaction.msg_id, "reaction": reaction.emoji}


@app.put("/channel/{chan_id}", tags=['Channels'])
def add_channel(chan_id: int, channel: Channel, token: str = Depends(token)):
    return {"name": channel.name}


@app.get("/channel/{chan_id}", tags=['Channels'])
def get_channel(chan_id: int):
    return chan_id


@app.patch("/channel/{chan_id}", tags=['Channels'])
def update_channel(chan_id: int, channel: Channel, token: str = Depends(token)):
    return {"name": channel.name}


@app.post("/voice_event", tags=["Events"])
def add_voice_event(event: VoiceEvent, token: str = Depends(token)):
    return {"user": event.user_id, "action": event.type, "time": event.timestamp}
