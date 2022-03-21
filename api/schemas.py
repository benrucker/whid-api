from datetime import date, datetime
from pydantic import BaseModel, HttpUrl

from .enums import VoiceEventType


class AttachmentBase(BaseModel):
    msg_id: str
    url: HttpUrl


class AttachmentCreate(AttachmentBase):
    pass


class Mention(BaseModel):
    msg_id: str
    mention: str
    type: str

    class Config:
        orm_mode = True


class Attachment(AttachmentBase):
    class Config:
        orm_mode = True


class MessageBase(BaseModel):
    id: str
    timestamp: datetime
    content: str
    attachments: list[Attachment] | None = None
    author: str
    replying_to: str | None = None
    channel: str
    mentions: list[Mention] | None = None
    edited: bool = False
    edited_timestamp: datetime | None = None
    deleted: bool = False
    deleted_timestamp: datetime | None = None
    pinned: bool = False


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    class Config:
        orm_mode = True


class MessageUpdate(BaseModel):
    content: str | None
    mentions: list[Mention] | None
    edited: bool | None = True
    edited_timestamp: datetime | None
    deleted: bool | None
    deleted_timestamp: datetime | None
    pinned: bool | None

    class Config:
        orm_mode = True


class ReactionBase(BaseModel):
    user_id: str
    msg_id: str
    emoji: str
    timestamp: datetime


class ReactionDelete(BaseModel):
    user_id: str
    msg_id: str
    emoji: str


class ReactionCreate(ReactionBase):
    pass


class Reaction(ReactionBase):
    class Config:
        orm_mode = True


class ChannelBase(BaseModel):
    id: str
    name: str
    category: str | None = None
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
    user_id: str
    type: VoiceEventType
    channel: str
    timestamp: datetime

    class Config:
        orm_mode = True


class VoiceEventCreate(VoiceEventBase):
    pass


class VoiceEvent(VoiceEventBase):
    pass


class ScoreBase(BaseModel):
    epoch: int
    user_id: str
    score: int


class ScoreCreate(ScoreBase):
    pass


class Score(ScoreBase):
    date_processed: date

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    id: str
    username: str
    nickname: str | None = None
    numbers: str

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: str | None
    nickname: str | None
    numbers: str | None

    class Config:
        orm_mode = True


class User(UserBase):
    messages: list[Message]
    scores: list[Score]


class Epoch(BaseModel):
    id: int
    start: datetime
    end: datetime

    class Config:
        orm_mode = True