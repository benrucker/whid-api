from datetime import date
from pydantic import BaseModel


class AttachmentBase(BaseModel):
    msg_id: int
    url: str


class AttachmentCreate(AttachmentBase):
    pass


class Attachment(AttachmentBase):
    class Config:
        orm_mode = True


class MessageBase(BaseModel):
    id: int
    timestamp: str
    content: str
    attachments: list[Attachment]
    author: int
    replying_to: int | None = None
    edited: bool = False
    edited_timestamp: int | None = None
    deleted: bool = False


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    class Config:
        orm_mode = True


class ReactionBase(BaseModel):
    user_id: int
    msg_id: int
    emoji: str


class ReactionCreate(ReactionBase):
    pass


class Reaction(ReactionBase):
    class Config:
        orm_mode = True


class ChannelBase(BaseModel):
    chan_id: int
    name: str
    category: str
    thread: bool = False


class ChannelCreate(ChannelBase):
    pass


class Channel(ChannelBase):
    class Config:
        orm_mode = True


class VoiceEventBase(BaseModel):
    user_id: int
    type: str
    timestamp: str


class VoiceEventCreate(VoiceEventBase):
    pass


class VoiceEvent(VoiceEventBase):
    class Config:
        orm_mode = True


class UserBase(BaseModel):
    user_id: int
    username: str
    nickname: str | None = None
    numbers: int


class UserCreate(UserBase):
    pass


class User(UserBase):
    class Config:
        orm_mode = True


class ScoreBase(BaseModel):
    iteration: int
    user_id: int
    date_processed: date
    score: int


class ScoreCreate(ScoreBase):
    pass


class Score(ScoreBase):
    class Config:
        orm_mode = True
