from sqlalchemy.orm import Session

from . import models, schemas


def get_message(db: Session, message_id: int):
    db_msg = db.query(models.Message).filter(models.Message.id == message_id).first()
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


def update_message(db: Session, message_id: int, message: schemas.MessageUpdate):
    db_message = get_message(db, message_id)
    if db_message is None:
        raise KeyError()
    for attr, value in message.items():
        setattr(db_message, attr, value)
    db.commit()
    db.refresh(db_message)
    return db_message


def delete_message(db: Session, message_id: int):
    db_message = get_message(db, message_id)
    if db_message is None:
        raise KeyError()
    db.delete(db_message)
    db.commit()
    return db_message


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def add_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        **user.dict(),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: schemas.User):
    db_user = get_user(db, user_id)
    if db_user is None:
        raise KeyError()
    for attr, value in user.dict().items():
        setattr(db_user, attr, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_score(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user is None:
        raise KeyError()
    return user.scores.order_by(models.Score.iteration.desc()).first()


def add_reaction(db: Session, reaction: schemas.Reaction):
    db_reaction = models.Reaction(
        **reaction.dict(),
    )
    db.add(db_reaction)
    db.commit()
    db.refresh(db_reaction)
    return db_reaction


def delete_reaction(db: Session, reaction: schemas.Reaction):
    db_reaction = db.query(models.Reaction) \
        .filter(models.Reaction.msg_id == reaction.msg_id) \
        .filter(models.Reaction.user_id == reaction.user_id) \
        .filter(models.Reaction.emoji == reaction.emoji) \
        .first()
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
    return db.query(models.Channel).filter(models.Channel.id == channel_id).first()


def update_channel(db: Session, channel_id: int, channel: schemas.Channel):
    db_channel = get_channel(db, channel_id)
    if db_channel is None:
        raise KeyError()
    for attr, value in channel.dict().items():
        setattr(db_channel, attr, value)
    db.commit()
    db.refresh(db_channel)
    return db_channel


def delete_channel(db: Session, channel_id: int):
    db_channel = get_channel(db, channel_id)
    if db_channel is None:
        raise KeyError()
    db.delete(db_channel)
    db.commit()
    return db_channel


def add_voice_event(db: Session, voice_event: schemas.VoiceEvent):
    db_voice_event = models.VoiceEvent(
        **voice_event.dict(),
    )
    db.add(db_voice_event)
    db.commit()
    db.refresh(db_voice_event)
    return db_voice_event



