from PySide6 import QtWidgets, QtGui, QtCore
from pathlib import Path
from typing import Optional, Any
from core.components.bases.base_component import BaseComponent


class BaseContextMenu(QtWidgets.QMenu):
    """
    Classe base para menus de contexto utilizando BaseComponent por composição
    para gerenciamento e resolução unificada de dependências via contexto.
    """

    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        context: Optional[Any] = None,
        scene_manager: Optional[Any] = None
    ):
        super().__init__(parent)

        # Utiliza o BaseComponent por composição para gerenciar o contexto rigidamente
        self._logic = BaseComponent(context=context, parent=self)

        # Suporte opcional à retrocompatibilidade para injeção direta de scene_manager
        self._direct_scene_manager = scene_manager

        self.context_object_id: Optional[str] = None
        self.setup_menu()

    @property
    def context(self) -> Optional[Any]:
        """Retorna o contexto atual injetado via BaseComponent."""
        return self._logic.context if hasattr(self, '_logic') else None

    @property
    def scene_manager(self) -> Optional[Any]:
        """Retorna o scene_manager priorizando o argumento direto ou a lógica do BaseComponent."""
        if self._direct_scene_manager is not None:
            return self._direct_scene_manager
        return self._logic.scene_manager if hasattr(self, '_logic') else None

    @scene_manager.setter
    def scene_manager(self, value: Any) -> None:
        """Permite redefinir o scene_manager dinamicamente."""
        self._direct_scene_manager = value

    @property
    def tool_manager(self) -> Optional[Any]:
        """Atalho seguro para o tool_manager a partir do BaseComponent."""
        return self._logic.tool_manager if hasattr(self, '_logic') else None

    @property
    def event_bus(self) -> Optional[Any]:
        """Atalho seguro para o event_bus a partir do BaseComponent."""
        return self._logic.event_bus if hasattr(self, '_logic') else None

    def setup_menu(self) -> None:
        pass

    def create_action(
            self,
            text: str,
            callback,
            icon_path: Optional[Path] = None,
            shortcut: Optional[str] = None
    ) -> QtGui.QAction:
        action = QtGui.QAction(text, self)
        if icon_path and icon_path.exists():
            action.setIcon(QtGui.QIcon(str(icon_path)))
        if shortcut:
            action.setShortcut(QtGui.QKeySequence(shortcut))
            action.setShortcutVisibleInContextMenu(True)
        action.triggered.connect(callback)
        self.addAction(action)
        return action

    def show_at_cursor(self, object_id: Optional[str] = None):
        self.context_object_id = object_id
        self.exec(QtGui.QCursor.pos())

    @property
    def has_scene(self) -> bool:
        return self.scene_manager is not None