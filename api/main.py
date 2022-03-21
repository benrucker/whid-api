from datetime import date, datetime
from typing import Union
from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
from .dependencies import get_db, token
from .exceptions import MissingReferencedDataException
from .enums import Epoch

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
        "name": "Members",
        "description": "Manage member metadata"
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


@app.exception_handler(MissingReferencedDataException)
async def missing_refs_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_424_FAILED_DEPENDENCY,
        content=exc.to_content()
    )


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/message", response_model=list[schemas.Message], tags=['Messages'])
def read_messages(member_id: str, epoch: Epoch | int | None = None, db: Session = Depends(get_db)):
    try:
        if epoch is None:
            return crud.get_messages_from_member(db, member_id)
        else:
            return crud.get_messages_from_member_during_epoch(db, member_id, epoch)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No messages found for member"
            + f" at epoch {epoch}" if epoch else ""
        )


@app.get("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'])
def read_message(msg_id: str, db: Session = Depends(get_db)):
    try:
        return crud.get_message(db, msg_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.put(
    "/message/{msg_id}",
    responses={
        200: {'model': schemas.Message},
        424: {'model': schemas.MissingData}
    },
    tags=['Messages']
)
def add_message(msg_id: str, message: schemas.MessageCreate, db: Session = Depends(get_db)):
    missing_members, missing_channels = get_missing_fields(message, db)

    if missing_members or missing_channels:
        raise MissingReferencedDataException(
            missing_members, missing_channels
        )

    db_msg = crud.add_message(db, message)
    return db_msg


def get_missing_fields(message, db):
    members = [message.author]
    if message.mentions:
        members = members + \
            list(
                map(
                    lambda x: x.mention, filter(
                        lambda x: x.type == "member", message.mentions
                    )
                )
            )

    missing_members = []
    for member in members:
        try:
            crud.get_member(db, member)
        except KeyError:
            missing_members.append(member)

    missing_channels = []
    try:
        crud.get_channel(db, message.channel)
    except KeyError:
        missing_channels.append(message.channel)
    return missing_members, missing_channels


@app.patch("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'])
def update_message(msg_id: str, message: schemas.MessageUpdate, db: Session = Depends(get_db)):
    try:
        return crud.update_message(db, msg_id, message.dict(exclude_unset=True))
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.delete("/message/{msg_id}", response_model=schemas.Message, tags=['Messages'])
def delete_message(msg_id: str, db: Session = Depends(get_db)):
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


@app.get("/member", response_model=list[schemas.Member], tags=['members'])
def get_all_members(db: Session = Depends(get_db)):
    try:
        return crud.get_all_members(db)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No members found"
        )


@app.get("/member/{member_id}", response_model=schemas.MemberBase, tags=["members"])
def get_member(member_id: str, db: Session = Depends(get_db)):
    try:
        return crud.get_member(db, member_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="member not found")


@app.put("/member/{member_id}", response_model=schemas.Member, tags=["members"])
def add_member(member_id: str, member: schemas.MemberCreate, db: Session = Depends(get_db)):
    return crud.add_member(db, member)


@app.patch("/member/{member_id}", response_model=schemas.Member, tags=["members"])
def update_member(member_id: str, data: schemas.MemberUpdate, db: Session = Depends(get_db)):
    try:
        return crud.update_member(db, member_id, data.dict(exclude_unset=True))
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="member not found")


@app.get("/scores", response_model=list[schemas.Score], tags=["Scores"])
def get_scores(epoch: Epoch | int = Epoch.CURR, db: Session = Depends(get_db)):
    try:
        return crud.get_scores(db, epoch)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No scores found for given epoch")


@app.get("/score", response_model=schemas.Score, tags=["Scores"])
def get_score(member_id: str, epoch: Epoch | int = Epoch.CURR, db: Session = Depends(get_db)):
    try:
        return crud.get_score(db, member_id, epoch)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No score found for given member and epoch")


@app.post("/scores", tags=["Scores"])
def add_scores(scores: list[schemas.ScoreCreate], db: Session = Depends(get_db)):
    crud.add_scores(db, scores)
    return f"success! {len(scores)} scores have been processed"


@app.post("/reaction", response_model=schemas.Reaction, tags=['Reactions'])
def add_reaction(reaction: schemas.Reaction, db: Session = Depends(get_db)):
    return crud.add_reaction(db, reaction)


@app.get("/reaction", response_model=list[schemas.Reaction], tags=['Reactions'])
def get_reactions(member_id: str, epoch: Epoch | int | None = None, db: Session = Depends(get_db)):
    try:
        if epoch:
            return crud.get_reactions_from_member_at_epoch(db, member_id, epoch)
        else:
            return crud.get_reactions_from_member(db, member_id)
    except KeyError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No reactions found for given member and epoch"
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
def add_channel(chan_id: str, channel: schemas.ChannelCreate, db: Session = Depends(get_db)):
    return crud.add_channel(db, channel)


@app.get("/channel/{chan_id}", response_model=schemas.Channel, tags=['Channels'])
def get_channel(chan_id: str, db: Session = Depends(get_db)):
    try:
        return crud.get_channel(db, chan_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")


@app.patch("/channel/{chan_id}", response_model=schemas.Channel, tags=['Channels'])
def update_channel(chan_id: str, channel: schemas.ChannelUpdate, db: Session = Depends(get_db)):
    try:
        return crud.update_channel(
            db, chan_id, channel.dict(exclude_unset=True)
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")


@app.delete("/channel/{chan_id}", response_model=schemas.Channel, tags=['Channels'])
def delete_channel(chan_id: str, db: Session = Depends(get_db)):
    try:
        return crud.delete_channel(db, chan_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")


@app.get("/voice_event", response_model=list[schemas.VoiceEvent], tags=['Misc Events'])
def get_voice_events(member: str, epoch: Epoch | int | None = None, db: Session = Depends(get_db)):
    try:
        if epoch:
            return crud.get_voice_events_during_epoch(db, member, epoch)
        else:
            return crud.get_voice_events(db, member)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Events not found")


@app.post("/voice_event", response_model=schemas.VoiceEvent, tags=["Misc Events"])
def add_voice_event(event: schemas.VoiceEvent, db: Session = Depends(get_db)):
    return crud.add_voice_event(db, event)


@app.get("/epoch/all", response_model=list[schemas.Epoch], tags=["Epochs"])
def get_epochs(db: Session = Depends(get_db)):
    try:
        return crud.get_epochs(db)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No epochs found"
        )


@app.get("/epoch/{epoch}", response_model=schemas.Epoch, tags=["Epochs"])
def get_epoch(epoch: Epoch | int, db: Session = Depends(get_db)):
    try:
        return crud.get_epoch(db, epoch)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Epoch not found"
        )
