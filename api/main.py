from datetime import date, datetime
from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
from .dependencies import get_db, token

tags = [
    {
        "name": "Scores",
        "description": "Add and retrieve scores"
    },
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
        "description": "Manage records of channels"
    },
    {
        "name": "Reactions",
        "description": "Add and remove reactions"
    },
    {
        "name": "Misc Events",
        "description": "Log other event types"
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


@app.get("/")
def read_root():
    return {"Hello": "World"}


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
    msg = crud.delete_message(db, msg_id)
    return msg


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
    db_user = crud.update_user(db, user_id, data.dict(exclude_unset=True))
    return db_user


@app.get("/score", response_model=schemas.Score, tags=["Scores"])
def get_user_score(user_id: int, db: Session = Depends(get_db)):
    score = crud.get_user_score(db, user_id)
    return score


@app.post("/score", tags=["Scores"])
def add_scores(scores: list[schemas.ScoreCreate], db: Session = Depends(get_db)):
    db_scores = crud.add_scores(db, scores)
    return db_scores


@app.post("/reaction", tags=['Reactions'])
def add_reaction(reaction: schemas.Reaction, db: Session = Depends(get_db)):
    return {"msg_id": reaction.msg_id, "user_id": reaction.msg_id, "reaction": reaction.emoji}


@app.delete('/reaction', tags=['Reactions'])
def delete_reaction(reaction: schemas.Reaction, db: Session = Depends(get_db)):
    return {"msg_id": reaction.msg_id, "user_id": reaction.msg_id, "reaction": reaction.emoji}


@app.put("/channel/{chan_id}", tags=['Channels'])
def add_channel(chan_id: int, channel: schemas.ChannelCreate, db: Session = Depends(get_db)):
    db_channel = crud.add_channel(db, channel)
    return db_channel


@app.get("/channel/{chan_id}", response_model=schemas.Channel, tags=['Channels'])
def get_channel(chan_id: int, db: Session = Depends(get_db)):
    try:
        db_channel = crud.get_channel(db, chan_id)
        return db_channel
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")


@app.patch("/channel/{chan_id}", tags=['Channels'])
def update_channel(chan_id: int, channel: schemas.ChannelUpdate, db: Session = Depends(get_db)):
    db_channel = crud.update_channel(db, chan_id, channel.dict(exclude_unset=True))
    return db_channel


@app.get("/voice_event", response_model=list[schemas.VoiceEvent], tags=['Misc Events'])
def get_voice_events(since: datetime, user: int, db: Session = Depends(get_db)):
    try:
        events = crud.get_voice_events(db, user, since)
        return events
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Events not found")


@app.post("/voice_event", response_model=schemas.VoiceEvent, tags=["Misc Events"])
def add_voice_event(event: schemas.VoiceEvent, db: Session = Depends(get_db)):
    db_event = crud.add_voice_event(db, event)
    return db_event


