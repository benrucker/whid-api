from datetime import date
from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
from .dependencies import get_db, token

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

try:
    models.Base.metadata.create_all(bind=engine)
except:
    pass

app = FastAPI(
    title="what have i done API",
    description="Yet another tool for Encouraging Extra-Effective Engagement!",
    openapi_tags=tags,
    dependencies=[Depends(token)]
)

@app.get("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'])
def read_message(msg_id: int, db: Session = Depends(get_db)):
    return {"item_id": msg_id}


@app.put("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'])
def add_message(msg_id: int, message: schemas.MessageCreate, db: Session = Depends(get_db)):
    return {"msg_id": msg_id, "message": message}


@app.patch("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'])
def update_message(msg_id: int, message: schemas.MessageCreate, db: Session = Depends(get_db)):
    # follow partial schema docs, search for 'patch'
    return message


@app.delete("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'])
def delete_message(msg_id: int, db: Session = Depends(get_db)):
    return {"msg_id": msg_id}


@app.put("/pin/{msg_id}", response_model=schemas.Message, tags=["Messages"])
def pin_message(msg_id, db: Session = Depends(get_db)):
    # use crud.update_message
    return f'pinned {msg_id}'


@app.get("/user/{user_id}", response_model=schemas.User, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    return {"user_id": user_id}


@app.put("/user/{user_id}", response_model=schemas.User, tags=["Users"])
def add_user(user_id: int, data: schemas.User, db: Session = Depends(get_db)):
    return {"user_id": user_id, "data": data}


@app.patch("/user/{user_id}", response_model=schemas.User, tags=["Users"])
def update_user(user_id: int, data: schemas.User, db: Session = Depends(get_db)):
    # TODO partial
    return {"user_id": user_id, "data": data}


@app.get("/user/{user_id}/score", tags=["Users"])
def get_user_score(user_id: int, db: Session = Depends(get_db)):
    return {"user_id": user_id, "score": 500}


@app.post("/reaction", tags=['Reactions'])
def add_reaction(reaction: schemas.Reaction, db: Session = Depends(get_db)):
    return {"msg_id": reaction.msg_id, "user_id": reaction.msg_id, "reaction": reaction.emoji}


@app.delete('/reaction', tags=['Reactions'])
def delete_reaction(reaction: schemas.Reaction, db: Session = Depends(get_db)):
    return {"msg_id": reaction.msg_id, "user_id": reaction.msg_id, "reaction": reaction.emoji}


@app.put("/channel/{chan_id}", tags=['Channels'])
def add_channel(chan_id: int, channel: schemas.Channel, db: Session = Depends(get_db)):
    return {"name": channel.name}


@app.get("/channel/{chan_id}", tags=['Channels'])
def get_channel(chan_id: int, db: Session = Depends(get_db)):
    return chan_id


@app.patch("/channel/{chan_id}", tags=['Channels'])
def update_channel(chan_id: int, channel: schemas.Channel, db: Session = Depends(get_db)):
    return {"name": channel.name}


@app.post("/voice_event", tags=["Events"])
def add_voice_event(event: schemas.VoiceEvent, db: Session = Depends(get_db)):
    return {"user": event.user_id, "action": event.type, "time": event.timestamp}
