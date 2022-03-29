from datetime import date, datetime
from pydantic import BaseModel, HttpUrl

from .enums import VoiceEventType, ChannelType


class MissingData(BaseModel):
    """
    Model for missing data.
    """

    missing_members: list[str]
    missing_channels: list[str]


class AttachmentBase(BaseModel):
    msg_id: str
    url: HttpUrl
    sticker: bool = False


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
    member_id: str
    msg_id: str
    emoji: str
    timestamp: datetime


class ReactionDelete(BaseModel):
    member_id: str
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
    type: ChannelType

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
    member_id: str
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
    member_id: str
    score: int


class ScoreCreate(ScoreBase):
    pass


class ScoreOut(ScoreBase):
    date: date
    class Config:
        orm_mode = True

class Score(ScoreBase):

    class Config:
        orm_mode = True


class MemberBase(BaseModel):
    id: str
    username: str
    nickname: str | None = None
    numbers: str
    bot: bool = False

    class Config:
        orm_mode = True


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    username: str | None
    nickname: str | None
    numbers: str | None

    class Config:
        orm_mode = True


class Member(MemberBase):
    messages: list[Message]
    scores: list[Score]


class Epoch(BaseModel):
    id: int
    start: datetime
    end: datetime

    class Config:
        orm_mode = True