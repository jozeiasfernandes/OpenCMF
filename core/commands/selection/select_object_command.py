from __future__ import annotations

from typing import List, Optional

from core.commands.base.command import Command
from core.scene.selection.selection_manager import (
    SelectionManager,
)


class SelectObjectCommand(Command):
    name = "select_object"

    def __init__(
        self,
        selection_manager: SelectionManager,
        object_id: str,
        exclusive: bool = True,
    ):
        super().__init__()

        self.selection_manager = selection_manager

        self.object_id = object_id
        self.exclusive = exclusive

        self._previous_selection: List[str] = []

    def can_execute(self) -> bool:
        return bool(self.object_id)

    def execute(self) -> bool:
        self._previous_selection = (
            self.selection_manager.selected_ids.copy()
        )

        self.selection_manager.select(
            obj_id=self.object_id,
            exclusive=self.exclusive,
        )

        return True

    def undo(self) -> bool:
        self.selection_manager.set_selection(
            self._previous_selection
        )

        return True


class ClearSelectionCommand(Command):
    name = "clear_selection"

    def __init__(
        self,
        selection_manager: SelectionManager,
    ):
        super().__init__()

        self.selection_manager = selection_manager

        self._previous_selection: List[str] = []

    def can_execute(self) -> bool:
        return bool(
            self.selection_manager.selected_ids
        )

    def execute(self) -> bool:
        self._previous_selection = (
            self.selection_manager.selected_ids.copy()
        )

        self.selection_manager.clear()

        return True

    def undo(self) -> bool:
        self.selection_manager.set_selection(
            self._previous_selection
        )

        return True


class ToggleSelectionCommand(Command):
    name = "toggle_selection"

    def __init__(
        self,
        selection_manager: SelectionManager,
        object_id: str,
    ):
        super().__init__()

        self.selection_manager = selection_manager

        self.object_id = object_id

        self._previous_state: Optional[bool] = None

    def can_execute(self) -> bool:
        return bool(self.object_id)

    def execute(self) -> bool:
        self._previous_state = (
            self.selection_manager.is_selected(
                self.object_id
            )
        )

        self.selection_manager.toggle(
            self.object_id
        )

        return True

    def undo(self) -> bool:
        current_state = (
            self.selection_manager.is_selected(
                self.object_id
            )
        )

        if current_state != self._previous_state:
            self.selection_manager.toggle(
                self.object_id
            )

        return True