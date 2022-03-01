from datetime import date, datetime
from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
from .dependencies import get_db, token
from .epoch import Epoch

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
    return crud.add_message(db, message)


@app.patch("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'])
def update_message(msg_id: int, message: schemas.MessageUpdate, db: Session = Depends(get_db)):
    try:
        return crud.update_message(db, msg_id, message.dict(exclude_unset=True))
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.delete("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'])
def delete_message(msg_id: int, db: Session = Depends(get_db)):
    try:
        return crud.delete_message(db, msg_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.put("/pin/{msg_id}", response_model=schemas.Message, tags=["Messages"])
def pin_message(msg_id, db: Session = Depends(get_db)):
    try:
        return crud.update_message(db, msg_id, {"pinned": True})
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.get("/user/{user_id}", response_model=schemas.UserBase, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_user(db, user_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.put("/user/{user_id}", response_model=schemas.User, tags=["Users"])
def add_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.add_user(db, user)


@app.patch("/user/{user_id}", response_model=schemas.User, tags=["Users"])
def update_user(user_id: int, data: schemas.UserUpdate, db: Session = Depends(get_db)):
    try:
        return crud.update_user(db, user_id, data.dict(exclude_unset=True))
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.get("/scores", response_model=list[schemas.Score], tags=["Scores"])
def get_scores(epoch: Epoch | int = Epoch.CURR, db: Session = Depends(get_db)):
    try:
        return crud.get_scores(db, epoch)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No scores found for given epoch")


@app.get("/score", response_model=schemas.Score, tags=["Scores"])
def get_score(user_id: int, epoch: Epoch | int = Epoch.CURR, db: Session = Depends(get_db)):
    try:
        return crud.get_score(db, user_id, epoch)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No score found for given user and epoch")


@app.post("/scores", tags=["Scores"])
def add_scores(scores: list[schemas.ScoreCreate], db: Session = Depends(get_db)):
    crud.add_scores(db, scores)
    return f"success! {len(scores)} scores have been processed"


@app.post("/reaction", response_model=schemas.Reaction, tags=['Reactions'])
def add_reaction(reaction: schemas.Reaction, db: Session = Depends(get_db)):
    return crud.add_reaction(db, reaction)


@app.get("/reaction", response_model=list[schemas.Reaction], tags=['Reactions'])
def get_reactions(user_id: int, epoch: Epoch | int = Epoch.CURR, db: Session = Depends(get_db)):
    try:
        return crud.get_reactions_from_user_at_epoch(db, user_id, epoch)
    except KeyError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No reactions found for given user and epoch"
        )


@app.delete('/reaction', tags=['Reactions'])
def delete_reaction(reaction: schemas.ReactionDelete, db: Session = Depends(get_db)):
    try:
        return crud.delete_reaction(db, reaction)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reaction not found"
        )


@app.put("/channel/{chan_id}", response_model=schemas.Channel, tags=['Channels'])
def add_channel(chan_id: int, channel: schemas.ChannelCreate, db: Session = Depends(get_db)):
    return crud.add_channel(db, channel)


@app.get("/channel/{chan_id}", response_model=schemas.Channel, tags=['Channels'])
def get_channel(chan_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_channel(db, chan_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")


@app.patch("/channel/{chan_id}", response_model=schemas.Channel, tags=['Channels'])
def update_channel(chan_id: int, channel: schemas.ChannelUpdate, db: Session = Depends(get_db)):
    try:
        return crud.update_channel(
            db, chan_id, channel.dict(exclude_unset=True)
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")


@app.delete("/channel/{chan_id}", response_model=schemas.Channel, tags=['Channels'])
def delete_channel(chan_id: int, db: Session = Depends(get_db)):
    try:
        return crud.delete_channel(db, chan_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")


@app.get("/voice_event", response_model=list[schemas.VoiceEvent], tags=['Misc Events'])
def get_voice_events(since: datetime, user: int, db: Session = Depends(get_db)):
    try:
        return crud.get_voice_events(db, user, since)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Events not found")


@app.post("/voice_event", response_model=schemas.VoiceEvent, tags=["Misc Events"])
def add_voice_event(event: schemas.VoiceEvent, db: Session = Depends(get_db)):
    return crud.add_voice_event(db, event)
