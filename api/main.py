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
    try:
        return crud.get_message(db, msg_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.put("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'])
def add_message(msg_id: int, message: schemas.MessageCreate, db: Session = Depends(get_db)):
    msg = crud.add_message(db, message)
    return msg


@app.patch("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'])
def update_message(msg_id: int, message: schemas.MessageUpdate, db: Session = Depends(get_db)):
    msg = crud.update_message(db, msg_id, message.dict(exclude_unset=True))
    return msg


@app.delete("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'])
def delete_message(msg_id: int, db: Session = Depends(get_db)):
    return {"msg_id": msg_id}


@app.put("/pin/{msg_id}", response_model=schemas.Message, tags=["Messages"])
def pin_message(msg_id, db: Session = Depends(get_db)):
    msg = crud.update_message(db, msg_id, {"pinned": True})
    return msg


@app.get("/user/{user_id}", response_model=schemas.UserBase, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = crud.get_user(db, user_id)
        return db_user
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.put("/user/{user_id}", response_model=schemas.User, tags=["Users"])
def add_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.add_user(db, user)
    return db_user


@app.patch("/user/{user_id}", response_model=schemas.User, tags=["Users"])
def update_user(user_id: int, data: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, user_id, data)
    return db_user


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
