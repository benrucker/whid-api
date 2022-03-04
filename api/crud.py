from datetime import date, datetime
from sqlalchemy.orm import Session

from . import models, schemas
from .enums import Epoch


def get_message(db: Session, message_id: int):
    db_msg = (
        db.query(models.Message)
        .filter(models.Message.id == message_id)
        .first()
    )
    if db_msg is None:
        raise KeyError()
    return db_msg


def add_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Message(
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


def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise KeyError()
    return user


def add_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        **user.dict(),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: dict):
    db_user = get_user(db, user_id)
    for attr, value in user.items():
        setattr(db_user, attr, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_scores(db: Session, epoch: Epoch | int):
    epoch = get_epoch(db, epoch).id
    scores = db.query(models.Score) \
               .filter(models.Score.epoch == epoch) \
               .all()
    if not scores:
        raise KeyError()
    return scores


def get_epoch(db: Session, epoch: Epoch | int):
    if not isinstance(epoch, int):
        if epoch is Epoch.CURR:
            epoch = get_current_epoch(db)
        elif epoch is Epoch.PREV:
            epoch = get_previous_epoch(db)
    db_epoch = db.query(models.Epoch).filter(models.Epoch.id == epoch).first()
    if not db_epoch:
        raise KeyError(f'No epoch found {epoch}')
    return db_epoch


def get_current_epoch(db: Session):
    now = datetime.now()
    epoch = (
        db.query(models.Epoch)
        .filter(
            models.Epoch.start <= now,
            now < models.Epoch.end
        ).first()
    )
    if epoch is None:
        raise KeyError('No current epoch at current time')
    return epoch.id


def get_previous_epoch(db: Session):
    prev = get_current_epoch(db) - 1
    if prev < 1:
        raise KeyError('No previous epoch')
    return prev


def get_score(db: Session, user_id: int, epoch: Epoch | int):
    epoch = get_epoch(db, epoch).id
    score = (
        db.query(models.Score)
        .filter(models.Score.epoch == epoch)
        .filter(models.Score.user_id == user_id)
        .first()
    )
    if not score:
        raise KeyError()
    return score


def add_scores(db: Session, scores: list[schemas.Score]):
    db.add_all(map(generate_score_model, scores))
    db.commit()


def generate_score_model(score: schemas.Score):
    return models.Score(
        **score.dict(),
        date_processed=date.today(),
    )


def get_reactions_from_user_at_epoch(db: Session, user_id: int, epoch: Epoch | int):
    epoch = get_epoch(db, epoch)
    reactions = (
        db.query(models.Reaction)
        .filter(
            models.Reaction.user_id == user_id,
            epoch.start <= models.Reaction.timestamp,
            models.Reaction.timestamp < epoch.end
        )
        .all()
    )
    if not reactions:
        raise KeyError()
    return reactions


def add_reaction(db: Session, reaction: schemas.Reaction):
    db_reaction = models.Reaction(
        **reaction.dict(),
    )
    db.add(db_reaction)
    db.commit()
    db.refresh(db_reaction)
    return db_reaction


def delete_reaction(db: Session, reaction: schemas.ReactionDelete):
    db_reaction = (
        db.query(models.Reaction)
        .filter(
            models.Reaction.msg_id == reaction.msg_id,
            models.Reaction.user_id == reaction.user_id,
            models.Reaction.emoji == reaction.emoji,
        )
        .first()
    )
    if db_reaction is None:
        raise KeyError()
    db.delete(db_reaction)
    db.commit()
    return db_reaction


def add_channel(db: Session, channel: schemas.ChannelCreate):
    db_channel = models.Channel(
        **channel.dict(),
    )
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel


def get_channel(db: Session, channel_id: int):
    db_chan = db.query(models.Channel).filter(
        models.Channel.id == channel_id).first()
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


def get_voice_events(db: Session, user_id: int, since: datetime):
    events = (
        db.query(models.VoiceEvent)
        .filter(
            models.VoiceEvent.user_id == user_id,
            models.VoiceEvent.timestamp >= since,
        )
        .all()
    )
    if not events:
        raise KeyError()
    return events


def add_voice_event(db: Session, voice_event: schemas.VoiceEvent):
    db_voice_event = models.VoiceEvent(
        **voice_event.dict(),
    )
    db.add(db_voice_event)
    db.commit()
    db.refresh(db_voice_event)
    return db_voice_event
