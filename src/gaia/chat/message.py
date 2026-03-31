from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ChatMessage:
    sender: str
    text: str
    timestamp: datetime
