from datetime import date, datetime
from pydantic import BaseModel, HttpUrl

from .enums import VoiceEventType


class AttachmentBase(BaseModel):
    msg_id: int
    url: HttpUrl


class AttachmentCreate(AttachmentBase):
    pass


class Attachment(AttachmentBase):
    class Config:
        orm_mode = True


class MessageBase(BaseModel):
    id: int
    timestamp: datetime
    content: str
    attachments: list[Attachment] | None = None
    author: int
    replying_to: int | None = None
    channel: int
    edited: bool = False
    edited_timestamp: datetime | None = None
    deleted: bool = False
    pinned: bool = False


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    class Config:
        orm_mode = True


class MessageUpdate(BaseModel):
    content: str | None
    edited: bool | None = True
    edited_timestamp: datetime | None
    deleted: bool | None
    pinned: bool | None

    class Config:
        orm_mode = True


class ReactionBase(BaseModel):
    user_id: int
    msg_id: int
    emoji: str
    timestamp: datetime


class ReactionDelete(BaseModel):
    user_id: int
    msg_id: int
    emoji: str


class ReactionCreate(ReactionBase):
    pass


class Reaction(ReactionBase):
    class Config:
        orm_mode = True


class ChannelBase(BaseModel):
    id: int
    name: str
    category: str
    thread: bool = False

    class Config:
        orm_mode = True


class ChannelCreate(ChannelBase):
    pass


class Channel(ChannelBase):
    messages: list[Message]


class ChannelUpdate(BaseModel):
    name: str | None
    category: str | None

    class Config:
        orm_mode = True


class VoiceEventBase(BaseModel):
    user_id: int
    type: VoiceEventType
    channel: int
    timestamp: datetime

    class Config:
        orm_mode = True


class VoiceEventCreate(VoiceEventBase):
    pass


class VoiceEvent(VoiceEventBase):
    pass


class ScoreBase(BaseModel):
    epoch: int
    user_id: int
    score: int


class ScoreCreate(ScoreBase):
    pass


class Score(ScoreBase):
    date_processed: date

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    id: int
    username: str
    nickname: str | None = None
    numbers: int

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: str | None
    nickname: str | None
    numbers: int | None

    class Config:
        orm_mode = True


class User(UserBase):
    messages: list[Message]
    scores: list[Score]


class Epoch(BaseModel):
    id: int
    start: datetime
    end: datetime
