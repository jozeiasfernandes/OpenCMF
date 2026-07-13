# core/components/toolbar_container/toolbar_container.py

from PySide6 import QtWidgets, QtCore
from typing import Dict, Optional


class ToolbarContainer(QtWidgets.QWidget):
    """
    Container visual que agrupa toolbars.
    Pode ser posicionado no topo ou na base da Workspace.
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(4)
        self.layout.setAlignment(QtCore.Qt.AlignLeft)

        self.toolbars: Dict[str, QtWidgets.QToolBar] = {}

    def add_toolbar(self, tb_id: str, toolbar: QtWidgets.QToolBar):
        self.layout.addWidget(toolbar)
        self.toolbars[tb_id] = toolbar

    def remove_toolbar(self, tb_id: str):
        if tb := self.toolbars.pop(tb_id, None):
            self.layout.removeWidget(tb)
            tb.setParent(None)