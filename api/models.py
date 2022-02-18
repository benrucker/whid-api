from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date
from sqlalchemy.orm import relationship

from .database import Base


class Message(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    content = Column(String)
    author = Column(Integer, ForeignKey("user.id"), nullable=False)
    replying_to = Column(Integer, ForeignKey("user.id"))
    edited = Column(Boolean)
    edited_timestamp = Column(DateTime)
    deleted = Column(Boolean, default=False, nullable=False)
    pinned = Column(Boolean, default=False, nullable=False)

    attachments = relationship("Attachments", back_populates="message")


class Attachment(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    message = Column(Integer, ForeignKey("message.id"), nullable=False)
    url = Column(String, nullable=False)


class Reaction(Base):
    message = Column(Integer, ForeignKey("message.id"), primary_key=True, nullable=False)
    user = Column(Integer, ForeignKey("user.id"), primary_key=True, nullable=False)
    emoji = Column(String, primary_key=True, nullable=False)


class Channel(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    thread = Column(Boolean, default=False, nullable=False)


class VoiceEvent(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    type = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)


class User(Base):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    nickname = Column(String)
    numbers = Column(String(4), nullable=False)

    messages = relationship("Message", back_populates="author")
    scores = relationship("Score", back_populates="user")
    reactions = relationship("Reaction", back_populates="user")


class Score(Base):
    iteration = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True, nullable=False)
    date_processed = Column(Date, nullable=False)
    score = Column(Integer, nullable=False)
