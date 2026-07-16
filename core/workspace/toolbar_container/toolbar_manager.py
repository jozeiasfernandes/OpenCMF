# core/components/toolbar_container/toolbar_manager.py

from PySide6 import QtWidgets, QtCore
from .toolbar_container import ToolbarContainer


from PySide6 import QtCore
# Certifique-se de importar ToolbarContainer se ele estiver em outro arquivo

class ToolbarManager(QtCore.QObject):
    def __init__(self):
        super().__init__()

        self.top_container = ToolbarContainer()
        self.bottom_container = ToolbarContainer()


    def register_toolbar(self, tb_id: str, toolbar: QtWidgets.QToolBar, to_top: bool = True):
        """Adiciona uma toolbar_container a um dos containers."""
        container = self.top_container if to_top else self.bottom_container
        container.add_toolbar(tb_id, toolbar)

    def move_toolbar(self, tb_id: str, to_top: bool):
        """Move uma toolbar_container entre topo e base sem destruí-la."""
        # 1. Encontra a toolbar_container atual
        tb = self.top_container.toolbars.get(tb_id) or self.bottom_container.toolbars.get(tb_id)
        if not tb:
            return

        # 2. Remove da origem e adiciona no destino
        if to_top:
            self.bottom_container.remove_toolbar(tb_id)
            self.top_container.add_toolbar(tb_id, tb)
        else:
            self.top_container.remove_toolbar(tb_id)
            self.bottom_container.add_toolbar(tb_id, tb)

    def set_toolbar_visible(self, tb_id: str, visible: bool):
        """Define a visibilidade de uma toolbar específica pelo seu ID."""
        # Busca a toolbar em qualquer um dos containers
        tb = self.top_container.toolbars.get(tb_id) or self.bottom_container.toolbars.get(tb_id)

        if tb:
            tb.setVisible(visible)

    def toggle_toolbar(self, tb_id: str):
        """Alterna a visibilidade de uma toolbar."""
        tb = self.top_container.toolbars.get(tb_id) or self.bottom_container.toolbars.get(tb_id)

        if tb:
            tb.setVisible(not tb.isVisible())

    def clear_all(self):
        """Remove todas as toolbars de ambos os containers."""
        # Limpa o topo
        for tb_id in list(self.top_container.toolbars.keys()):
            self.top_container.remove_toolbar(tb_id)

        # Limpa a base
        for tb_id in list(self.bottom_container.toolbars.keys()):
            self.bottom_container.remove_toolbar(tb_id)