from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import engine
from .dependencies import get_db, token
from .enums import Epoch
from .exceptions import MissingReferencedDataException

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
    schemas.Base.metadata.create_all(bind=engine)
except:
    pass

app = FastAPI(
    title="what have i done API",
    description="Yet another tool for Encouraging Extra-Effective Engagement!",
    openapi_tags=tags,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get(
    "/message",
    response_model=list[models.Message],
    tags=['Messages'],
    dependencies=[Depends(token)]
)
def read_messages(epoch: Epoch | int = Epoch.CURR, db: Session = Depends(get_db)):
    try:
        return crud.get_messages_during_epoch(db, epoch)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No messages found at epoch {epoch}"
        )


@app.get(
    "/message/{msg_id}",
    response_model=models.Message,
    tags=['Messages'],
    dependencies=[Depends(token)]
)
def read_message(msg_id: str, db: Session = Depends(get_db)):
    try:
        return crud.get_message(db, msg_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )


@app.put(
    "/message/{msg_id}",
    responses={
        200: {'model': models.Message},
        424: {'model': models.MissingData}
    },
    tags=['Messages'],
    dependencies=[Depends(token)]
)
def add_message(msg_id: str, message: models.MessageCreate, db: Session = Depends(get_db)):
    missing_members, missing_channels = get_missing_fields(message, db)

    if missing_members or missing_channels:
        raise MissingReferencedDataException(
            missing_members, missing_channels
        )

    db_msg = crud.add_message(db, message)
    return db_msg


def get_missing_fields(message, db):
    missing_members = get_missing_members(message, db)
    missing_channels = get_missing_channels(message, db)
    return list(missing_members), list(missing_channels)


def get_missing_channels(message, db, ):
    return filter_out_existing(db, [message.channel], crud.get_channel)


def get_missing_members(message, db):
    members = [message.author]
    if message.mentions:
        members = members + \
            [x.mention for x in message.mentions if x.type == "member"]
    if message.replying_to:
        members.append(message.replying_to)

    missing_members = filter_out_existing(db, members, crud.get_member)
    return missing_members


def filter_out_existing(db, members, getter):
    missing_members = set()
    for member in members:
        try:
            getter(db, member)
        except KeyError:
            missing_members.add(member)
    return missing_members


@app.patch(
    "/message/{msg_id}",
    response_model=models.Message,
    tags=['Messages'],
    dependencies=[Depends(token)]
)
def update_message(msg_id: str, message: models.MessageUpdate, db: Session = Depends(get_db)):
    try:
        return crud.update_message(db, msg_id, message.dict(exclude_unset=True))
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.delete(
    "/message/{msg_id}",
    response_model=models.Message,
    tags=['Messages'],
    dependencies=[Depends(token)]
)
def delete_message(msg_id: str, db: Session = Depends(get_db)):
    try:
        return crud.delete_message(db, msg_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.put(
    "/pin/{msg_id}",
    response_model=models.Message,
    tags=["Messages"],
    dependencies=[Depends(token)]
)
def pin_message(msg_id, db: Session = Depends(get_db)):
    try:
        return crud.update_message(db, msg_id, {"pinned": True})
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


@app.get(
    "/member",
    response_model=list[models.MemberBase],
    tags=['Members'],
    dependencies=[Depends(token)]
)
def get_all_members(db: Session = Depends(get_db)):
    try:
        return crud.get_all_members(db)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No members found"
        )


@app.get(
    "/member/{member_id}",
    response_model=models.MemberBase,
    tags=["Members"],
    dependencies=[Depends(token)]
)
def get_member(member_id: str, db: Session = Depends(get_db)):
    try:
        return crud.get_member(db, member_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="member not found")


@app.put(
    "/member/{member_id}",
    response_model=models.MemberBase,
    tags=["Members"],
    dependencies=[Depends(token)]
)
def add_member(member_id: str, member: models.MemberCreate, db: Session = Depends(get_db)):
    return crud.add_member(db, member)


@app.patch(
    "/member/{member_id}",
    response_model=models.MemberBase,
    tags=["Members"],
    dependencies=[Depends(token)]
)
def update_member(member_id: str, data: models.MemberUpdate, db: Session = Depends(get_db)):
    try:
        return crud.update_member(db, member_id, data.dict(exclude_unset=True))
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="member not found")


@app.get(
    "/member/{member_id}/scores",
    response_model=list[models.ScoreOut],
    tags=["Scores"],
)
def get_member_scores(member_id: str, db: Session = Depends(get_db)):
    try:
        return crud.get_scores_for_user_with_date(db, member_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No scores for member found"
        )


@app.get(
    "/member/name/{member_name}/scores",
    response_model=list[models.ScoreOut],
    tags=["Scores"],
)
def get_member_scores_by_name(member_name: str, db: Session = Depends(get_db)):
    try:
        return crud.get_scores_for_user_by_name_with_date(db, member_name)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No scores for member found"
        )


@app.get(
    "/scores",
    response_model=list[models.Score],
    tags=["Scores"],
)
def get_scores(epoch: Epoch | int = Epoch.CURR, db: Session = Depends(get_db)):
    try:
        return crud.get_scores(db, epoch)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No scores found for given epoch")


@app.get(
    "/score",
    response_model=models.Score,
    tags=["Scores"],
)
def get_score(member_id: str, epoch: Epoch | int = Epoch.CURR, db: Session = Depends(get_db)):
    try:
        return crud.get_score_for_user_during_epoch(db, member_id, epoch)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No score found for given member and epoch")


@app.post(
    "/scores",
    tags=["Scores"],
    dependencies=[Depends(token)]
)
def add_scores(scores: list[models.ScoreCreate], db: Session = Depends(get_db)):
    crud.add_scores(db, scores)
    return f"success! {len(scores)} scores have been processed"


@app.post(
    "/reaction",
    response_model=models.Reaction,
    tags=['Reactions'],
    dependencies=[Depends(token)]
)
def add_reaction(reaction: models.Reaction, db: Session = Depends(get_db)):
    return crud.add_reaction(db, reaction)


@app.get(
    "/reaction",
    response_model=list[models.Reaction],
    tags=['Reactions'],
    dependencies=[Depends(token)]
)
def get_reactions(member_id: str, epoch: Epoch | int | None = None, db: Session = Depends(get_db)):
    try:
        if epoch:
            return crud.get_reactions_from_member_during_epoch(db, member_id, epoch)
        else:
            return crud.get_reactions_from_member(db, member_id)
    except KeyError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No reactions found for given member and epoch"
        )


@app.delete(
    '/reaction',
    response_model=models.Reaction,
    tags=['Reactions'],
    dependencies=[Depends(token)]
)
def delete_reaction(reaction: models.ReactionDelete, db: Session = Depends(get_db)):
    try:
        return crud.delete_reaction(db, reaction)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reaction not found"
        )


@app.put(
    "/channel/{chan_id}",
    response_model=models.Channel,
    tags=['Channels'],
    dependencies=[Depends(token)]
)
def add_channel(chan_id: str, channel: models.ChannelCreate, db: Session = Depends(get_db)):
    return crud.add_channel(db, channel)


@app.get(
    "/channel/{chan_id}",
    response_model=models.Channel,
    tags=['Channels'],
    dependencies=[Depends(token)]
)
def get_channel(chan_id: str, db: Session = Depends(get_db)):
    try:
        return crud.get_channel(db, chan_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")


@app.patch(
    "/channel/{chan_id}",
    response_model=models.Channel,
    tags=['Channels'],
    dependencies=[Depends(token)]
)
def update_channel(chan_id: str, channel: models.ChannelUpdate, db: Session = Depends(get_db)):
    try:
        return crud.update_channel(
            db, chan_id, channel.dict(exclude_unset=True)
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")


@app.delete(
    "/channel/{chan_id}",
    response_model=models.Channel,
    tags=['Channels'],
    dependencies=[Depends(token)]
)
def delete_channel(chan_id: str, db: Session = Depends(get_db)):
    try:
        return crud.delete_channel(db, chan_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")


@app.get(
    "/voice_event",
    response_model=list[models.VoiceEvent],
    tags=['Misc Events'],
    dependencies=[Depends(token)]
)
def get_voice_events(epoch: Epoch | int = Epoch.CURR, db: Session = Depends(get_db)):
    try:
        return crud.get_voice_events_during_epoch(db, epoch)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Events not found")


@app.post(
    "/voice_event",
    response_model=models.VoiceEvent,
    tags=["Misc Events"],
    dependencies=[Depends(token)]
)
def add_voice_event(event: models.VoiceEvent, db: Session = Depends(get_db)):
    missing_members, missing_channels = get_missing_fields_from_event(
        db, event)

    if missing_members or missing_channels:
        raise MissingReferencedDataException(
            list(missing_members), list(missing_channels)
        )

    return crud.add_voice_event(db, event)


def get_missing_fields_from_event(db: Session, event: models.VoiceEvent):
    missing_channels = filter_out_existing(
        db, [event.channel], crud.get_channel)
    missing_members = filter_out_existing(
        db, [event.member_id], crud.get_member)
    return missing_members, missing_channels


@app.get(
    "/epoch/all",
    response_model=list[models.Epoch],
    tags=["Epochs"],
    dependencies=[Depends(token)]
)
def get_epochs(db: Session = Depends(get_db)):
    try:
        return crud.get_epochs(db)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No epochs found"
        )


@app.get(
    "/epoch/{epoch}",
    response_model=models.Epoch,
    tags=["Epochs"],
    dependencies=[Depends(token)]
)
def get_epoch(epoch: Epoch | int, db: Session = Depends(get_db)):
    try:
        return crud.get_epoch(db, epoch)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Epoch not found"
        )
