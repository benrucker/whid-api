from datetime import date
from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

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

models.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="what have i done API",
    description="Yet another tool for Encouraging Extra-Effective Engagement!",
    openapi_tags=tags,
)
auth_scheme = HTTPBearer()
with open('.usertokens') as f:
    usertokens = f.readlines()


def token(creds: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if creds.credentials not in usertokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'])
def read_message(msg_id: int, db: Session = Depends(get_db)):
    return {"item_id": msg_id}


@app.put("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'], dependencies=[token])
def add_message(msg_id: int, message: schemas.MessageCreate):
    return {"msg_id": msg_id, "message": message}


@app.patch("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'], dependencies=[token])
def update_message(msg_id: int, message: schemas.MessageCreate):
    # follow partial schema docs, search for 'patch'
    # 
    return message


@app.delete("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'], dependencies=[token])
def delete_message(msg_id: int):
    return {"msg_id": msg_id}


@app.put("/pin/{msg_id}", response_model=schemas.Message, tags=["Messages"], dependencies=[token])
def pin_message(msg_id):
    # use crud.update_message
    return f'pinned {msg_id}'


@app.get("/user/{user_id}", response_model=schemas.User, tags=["Users"])
def get_user(user_id: int):
    return {"user_id": user_id}


@app.put("/user/{user_id}", response_model=schemas.User, tags=["Users"], dependencies=[token])
def add_user(user_id: int, data: schemas.User):
    return {"user_id": user_id, "data": data}


@app.patch("/user/{user_id}", response_model=schemas.User, tags=["Users"], dependencies=[token])
def update_user(user_id: int, data: schemas.User):
    # TODO partial
    return {"user_id": user_id, "data": data}


@app.get("/user/{user_id}/score", tags=["Users"])
def get_user_score(user_id: int):
    return {"user_id": user_id, "score": 500}


@app.post("/reaction", tags=['Reactions'], dependencies=[token])
def add_reaction(reaction: schemas.Reaction):
    return {"msg_id": reaction.msg_id, "user_id": reaction.msg_id, "reaction": reaction.emoji}


@app.delete('/reaction', tags=['Reactions'], dependencies=[token])
def delete_reaction(reaction: schemas.Reaction):
    return {"msg_id": reaction.msg_id, "user_id": reaction.msg_id, "reaction": reaction.emoji}


@app.put("/channel/{chan_id}", tags=['Channels'], dependencies=[token])
def add_channel(chan_id: int, channel: schemas.Channel):
    return {"name": channel.name}


@app.get("/channel/{chan_id}", tags=['Channels'])
def get_channel(chan_id: int):
    return chan_id


@app.patch("/channel/{chan_id}", tags=['Channels'], dependencies=[token])
def update_channel(chan_id: int, channel: schemas.Channel):
    return {"name": channel.name}


@app.post("/voice_event", tags=["Events"], dependencies=[token])
def add_voice_event(event: schemas.VoiceEvent):
    return {"user": event.user_id, "action": event.type, "time": event.timestamp}
