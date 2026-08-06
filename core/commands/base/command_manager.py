from __future__ import annotations

from typing import List, Optional

from commands.base.command import Command


class CommandManager:
    def __init__(self, max_history: int = 100):
        self.max_history = max_history

        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []

    @property
    def undo_count(self) -> int:
        return len(self._undo_stack)

    @property
    def redo_count(self) -> int:
        return len(self._redo_stack)

    @property
    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    @property
    def last_command(self) -> Optional[Command]:
        if not self._undo_stack:
            return None

        return self._undo_stack[-1]

    def execute(
        self,
        command: Command,
    ) -> bool:
        if not command.can_execute():
            return False

        success = command.execute()

        if not success:
            return False

        command.mark_executed()

        self._undo_stack.append(command)

        self._redo_stack.clear()

        self._trim_history()

        return True

    def undo(self) -> bool:
        if not self._undo_stack:
            return False

        command = self._undo_stack.pop()

        if not command.can_undo():
            self._undo_stack.append(command)
            return False

        success = command.undo()

        if not success:
            self._undo_stack.append(command)
            return False

        command.mark_undone()

        self._redo_stack.append(command)

        return True

    def redo(self) -> bool:
        if not self._redo_stack:
            return False

        command = self._redo_stack.pop()

        success = command.redo()

        if not success:
            self._redo_stack.append(command)
            return False

        command.mark_executed()

        self._undo_stack.append(command)

        return True

    def clear(self) -> None:
        self._undo_stack.clear()
        self._redo_stack.clear()

    def _trim_history(self) -> None:
        if len(self._undo_stack) <= self.max_history:
            return

        overflow = len(self._undo_stack) - self.max_history

        del self._undo_stack[:overflow]