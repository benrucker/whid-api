from sqlalchemy.orm import Session

from . import models, schemas


def get_message(db: Session, message_id: int):
    return db.query(models.Message).filter(models.Message.id == message_id).first()


def add_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Message(
        **message.dict(),
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
