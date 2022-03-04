
from enum import Enum

class Epoch(str, Enum):
    CURR = "current"
    PREV = "previous"


class VoiceEventType(str, Enum):
    JOIN = "join"
    LEAVE = "leave"
    MOVE = "move"
    DEAF = "deafen"
    UNDEAF = "undeafen"
    MUTE = "mute"
    UNMUTE = "unmute"
    SERVER_DEAF = "server deafen"
    SERVER_UNDEAF = "server undeafen"
    SERVER_MUTE = "server mute"
    SERVER_UNMUTE = "server unmute"
    WEBCAM_START = "webcam start"
    WEBCAM_STOP = "webcam stop"
    STREAM_START = "stream start"
    STREAM_STOP = "stream stop"
