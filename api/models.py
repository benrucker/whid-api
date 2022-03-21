from sqlite3 import Timestamp
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date
from sqlalchemy.orm import relationship

from .database import Base


class Message(Base):
    __tablename__ = "message"

    id = Column(String, primary_key=True, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    content = Column(String)
    author = Column(String, ForeignKey("member.id"), nullable=False)
    replying_to = Column(String, ForeignKey("member.id"))
    channel = Column(String, ForeignKey("channel.id"), nullable=False)
    edited = Column(Boolean)
    edited_timestamp = Column(DateTime)
    deleted = Column(Boolean, default=False, nullable=False)
    deleted_timestamp = Column(DateTime)
    pinned = Column(Boolean, default=False, nullable=False)

    mentions = relationship("Mention", primaryjoin="Mention.msg_id == Message.id")
    attachments = relationship("Attachment")
    epoch = relationship(
        "Epoch",
        primaryjoin="and_(remote(Epoch.start) <= Message.timestamp, Message.timestamp < remote(Epoch.end))",
        foreign_keys=timestamp,
        remote_side="Epoch.id",
        viewonly=True,
    )


class Mention(Base):
    __tablename__ = "mention"

    id = Column(Integer, primary_key=True, nullable=False)
    msg_id = Column(String, ForeignKey("message.id"), nullable=False)
    mention = Column(String, nullable=False)
    type = Column(String, nullable=False)


class Attachment(Base):
    __tablename__ = "attachment"

    id = Column(Integer, primary_key=True, nullable=False)
    msg_id = Column(String, ForeignKey("message.id"), nullable=False)
    url = Column(String, nullable=False)


class Reaction(Base):
    __tablename__ = "reaction"

    msg_id = Column(String, ForeignKey("message.id"),
                     primary_key=True, nullable=False)
    member_id = Column(String, ForeignKey("member.id"),
                  primary_key=True, nullable=False)
    emoji = Column(String, primary_key=True, nullable=False)
    timestamp = Column(DateTime)


class Channel(Base):
    __tablename__ = "channel"

    id = Column(String, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String)
    thread = Column(Boolean, default=False, nullable=False)

    messages = relationship("Message")


class VoiceEvent(Base):
    __tablename__ = "voice_event"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    member_id = Column(String, ForeignKey("member.id"), nullable=False)
    type = Column(String, nullable=False)
    channel = Column(String, ForeignKey("channel.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)


class Member(Base):
    __tablename__ = "member"

    id = Column(String, primary_key=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    nickname = Column(String)
    numbers = Column(String(4), nullable=False)

    messages = relationship("Message", foreign_keys=[Message.author])
    scores = relationship("Score")
    reactions = relationship("Reaction")


class Score(Base):
    __tablename__ = "score"

    epoch = Column(Integer, primary_key=True, index=True, nullable=False)
    member_id = Column(String, ForeignKey("member.id"),
                     primary_key=True, nullable=False)
    date_processed = Column(Date, nullable=False)
    score = Column(Integer, nullable=False)


class Epoch(Base):
    __tablename__ = "epoch"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
