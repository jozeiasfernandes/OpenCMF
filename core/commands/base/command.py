from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass(slots=True)
class CommandMetadata:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    source: Optional[str] = None
    description: Optional[str] = None


class Command(ABC):
    name = "command"

    def __init__(self):
        self.metadata = CommandMetadata()

        self.executed = False

    @abstractmethod
    def execute(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def undo(self) -> bool:
        raise NotImplementedError

    def redo(self) -> bool:
        return self.execute()

    def can_execute(self) -> bool:
        return True

    def can_undo(self) -> bool:
        return self.executed

    def mark_executed(self) -> None:
        self.executed = True

    def mark_undone(self) -> None:
        self.executed = False