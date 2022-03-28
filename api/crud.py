from datetime import date, datetime
from sqlalchemy.orm import Session

from . import models, schemas
from .enums import Epoch
from .settings import get_settings


def get_message(db: Session, message_id: int):
    db_msg = (
        db.query(schemas.Message)
        .filter(schemas.Message.id == message_id)
        .first()
    )
    if db_msg is None:
        raise KeyError()
    return db_msg


def get_messages_from_member(db: Session, member_id: int):
    messages = (
        db.query(schemas.Message)
        .filter(schemas.Message.author == member_id)
        .all()
    )
    if not messages:
        raise KeyError()
    return messages


def get_messages_during_epoch(db: Session, epoch: Epoch | int):
    epoch = get_epoch(db, epoch)
    print(datetime.now())
    print(epoch)
    messages = (
        db.query(schemas.Message)
        .filter(
            schemas.Message.epoch == epoch,
        )
        .all()
    )
    if not messages:
        raise KeyError()
    return messages


def add_message(db: Session, message: models.MessageCreate):
    db_message = schemas.Message(
        **message.dict(),
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def update_message(db: Session, message_id: int, message: dict):
    db_message = get_message(db, message_id)
    for attr, value in message.items():
        setattr(db_message, attr, value)
    db.commit()
    db.refresh(db_message)
    return db_message


def delete_message(db: Session, message_id: int):
    db_message = get_message(db, message_id)
    db.delete(db_message)
    db.commit()
    return db_message


def get_all_members(db: Session):
    members = db.query(schemas.Member).all()
    if not members:
        raise KeyError()
    return members


def get_member(db: Session, member_id: int):
    member = db.query(schemas.Member).filter(schemas.Member.id == member_id).first()
    if member is None:
        raise KeyError()
    return member


def add_member(db: Session, member: models.MemberCreate):
    db_member = schemas.Member(
        **member.dict(),
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    add_default_score_if_necessary(db, db_member.id)
    return db_member


def add_default_score_if_necessary(db: Session, member_id: int):
    try:
        get_scores_for_user(db, member_id)
        print('got score for user', member_id)
    except: 
        db.add(schemas.Score(
            member_id=member_id,
            epoch=get_current_epoch(db),
            score=get_settings().default_score,
        ))
        db.commit()


def update_member(db: Session, member_id: int, member: dict):
    db_member = get_member(db, member_id)
    for attr, value in member.items():
        setattr(db_member, attr, value)
    db.commit()
    db.refresh(db_member)
    return db_member


def get_scores(db: Session, epoch: Epoch | int):
    epoch = get_epoch(db, epoch).id
    scores = db.query(schemas.Score) \
               .filter(schemas.Score.epoch == epoch) \
               .all()
    if not scores:
        raise KeyError()
    return scores


def get_epochs(db: Session):
    epochs = db.query(schemas.Epoch).all()
    if not epochs or len(epochs) == 0:
        raise KeyError()
    return epochs


def get_epoch(db: Session, epoch: Epoch | int):
    epoch = epoch_to_int(db, epoch)

    db_epoch = db.query(schemas.Epoch).filter(schemas.Epoch.id == epoch).first()
    if not db_epoch:
        raise KeyError(f'No epoch found {epoch}')
    return db_epoch


def epoch_to_int(db: Session, epoch: Epoch | int):
    match epoch:
        case Epoch.CURR:
            epoch = get_current_epoch(db)
        case Epoch.PREV:
            epoch = get_previous_epoch(db)
        case int:
            pass
    return epoch


def get_current_epoch(db: Session):
    now = datetime.now()
    epoch = (
        db.query(schemas.Epoch)
        .filter(
            schemas.Epoch.start <= now,
            now < schemas.Epoch.end
        ).first()
    )
    if epoch is None:
        raise KeyError('No epoch at current time')
    return epoch.id


def get_previous_epoch(db: Session):
    prev = get_current_epoch(db) - 1
    if prev < 1:
        raise KeyError('No previous epoch')
    return prev


def get_score_for_user_during_epoch(db: Session, member_id: int, epoch: Epoch | int):
    epoch = get_epoch(db, epoch).id
    score = (
        db.query(schemas.Score)
        .filter(schemas.Score.epoch == epoch)
        .filter(schemas.Score.member_id == member_id)
        .first()
    )
    if not score:
        raise KeyError()
    return score


def get_scores_for_user(db: Session, member_id: int):
    db_score = (
        db.query(schemas.Score)
        .filter(schemas.Score.member_id == member_id)
    ).all()
    if not db_score:
        raise KeyError("No score for user")
    return db_score


def add_scores(db: Session, scores: list[models.Score]):
    db.add_all(map(generate_score_model, scores))
    db.commit()


def generate_score_model(score: models.Score):
    return schemas.Score(
        **score.dict(),
    )


def get_reactions_from_member(db: Session, member_id: int):
    reactions = (
        db.query(schemas.Reaction)
        .filter(schemas.Reaction.member_id == member_id)
        .all()
    )
    if not reactions:
        raise KeyError()
    return reactions


def get_reactions_from_member_during_epoch(db: Session, member_id: int, epoch: Epoch | int):
    epoch = get_epoch(db, epoch)
    reactions = (
        db.query(schemas.Reaction)
        .filter(
            schemas.Reaction.member_id == member_id,
            epoch.start <= schemas.Reaction.timestamp,
            schemas.Reaction.timestamp < epoch.end
        )
        .all()
    )
    if not reactions:
        raise KeyError()
    return reactions


def add_reaction(db: Session, reaction: models.Reaction):
    db_reaction = schemas.Reaction(
        **reaction.dict(),
    )
    db.add(db_reaction)
    db.commit()
    db.refresh(db_reaction)
    return db_reaction


def delete_reaction(db: Session, reaction: models.ReactionDelete):
    db_reaction = (
        db.query(schemas.Reaction)
        .filter(
            schemas.Reaction.msg_id == reaction.msg_id,
            schemas.Reaction.member_id == reaction.member_id,
            schemas.Reaction.emoji == reaction.emoji,
        )
        .first()
    )
    if db_reaction is None:
        raise KeyError()
    db.delete(db_reaction)
    db.commit()
    return db_reaction


def add_channel(db: Session, channel: models.ChannelCreate):
    db_channel = schemas.Channel(
        **channel.dict(),
    )
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel


def get_channel(db: Session, channel_id: int):
    db_chan = db.query(schemas.Channel).filter(
        schemas.Channel.id == channel_id).first()
    if db_chan is None:
        raise KeyError()
    return db_chan


def update_channel(db: Session, channel_id: int, channel: dict):
    db_channel = get_channel(db, channel_id)
    for attr, value in channel.items():
        setattr(db_channel, attr, value)
    db.commit()
    db.refresh(db_channel)
    return db_channel


def delete_channel(db: Session, channel_id: int):
    db_channel = get_channel(db, channel_id)
    db.delete(db_channel)
    db.commit()
    return db_channel


def get_voice_events(db: Session, member_id: int):
    events = (
        db.query(schemas.VoiceEvent)
        .filter(
            schemas.VoiceEvent.member_id == member_id,
        )
        .all()
    )
    if not events:
        raise KeyError()
    return events


def get_voice_events_during_epoch(db: Session, epoch: Epoch | int):
    epoch = get_epoch(db, epoch)
    events = (
        db.query(schemas.VoiceEvent)
        .filter(
            epoch.start <= schemas.VoiceEvent.timestamp,
            schemas.VoiceEvent.timestamp < epoch.end
        )
        .all()
    )
    if not events:
        raise KeyError(f"No voice events found at epoch {epoch}")
    return events


def add_voice_event(db: Session, voice_event: models.VoiceEvent):
    db_voice_event = schemas.VoiceEvent(
        **voice_event.dict(),
    )
    db.add(db_voice_event)
    db.commit()
    db.refresh(db_voice_event)
    return db_voice_event
