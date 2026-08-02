# Lógica de controle das abas
# Adicionar, remover, ordenar, ativar e sincronizar com o QStackedWidget.

from PySide6 import QtWidgets, QtCore
from core.workspace.module_manager.workspace_tab_widget import WorkspaceTabWidget


class TabController(QtCore.QObject):
    tab_changed = QtCore.Signal(int)
    tab_closed = QtCore.Signal(int)

    def __init__(self, container: QtWidgets.QStackedWidget):
        super().__init__()
        self.container = container
        # Usamos uma lista para manter a ordem visual
        self.tabs: list[WorkspaceTabWidget] = []
        # Mapa para garantir que sempre saibamos qual widget pertence a qual aba
        self._tab_to_widget: dict[WorkspaceTabWidget, QtWidgets.QWidget] = {}

        self.tab_bar_layout = QtWidgets.QHBoxLayout()
        self.tab_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_bar_layout.setSpacing(2)
        self.tab_bar_layout.addStretch()  # Mantém as abas alinhadas à esquerda

    def add_tab(self, title: str, content_widget: QtWidgets.QWidget):
        tab = WorkspaceTabWidget(title)

        # Conexões seguras utilizando o índice atual dinamicamente
        tab.close_requested.connect(lambda t=tab: self._handle_close(t))
        tab.clicked.connect(lambda t=tab: self._on_tab_clicked(t))

        self.tabs.append(tab)
        self._tab_to_widget[tab] = content_widget

        self.container.addWidget(content_widget)
        # Insere antes do stretch
        self.tab_bar_layout.insertWidget(self.tab_bar_layout.count() - 1, tab)

        # Se for a primeira aba, ativa-a automaticamente
        if len(self.tabs) == 1:
            self.set_active(0)

    def _on_tab_clicked(self, tab: WorkspaceTabWidget):
        if tab in self.tabs:
            index = self.tabs.index(tab)
            self.set_active(index)

    def _handle_close(self, tab: WorkspaceTabWidget):
        if tab not in self.tabs:
            return

        index = self.tabs.index(tab)
        widget = self._tab_to_widget.pop(tab)
        self.tabs.remove(tab)

        # Remove do Container e limpa da pilha de forma segura
        self.container.removeWidget(widget)
        widget.deleteLater()

        # Remove visualmente
        self.tab_bar_layout.removeWidget(tab)
        tab.deleteLater()

        self.tab_closed.emit(index)

        # Ajusta a aba ativa para a anterior ou próxima
        if self.tabs:
            new_index = max(0, index - 1)
            self.set_active(new_index)

    def set_active(self, index: int):
        if not (0 <= index < len(self.tabs)):
            return

        for i, tab in enumerate(self.tabs):
            tab.set_active(i == index)

        # Mapeia a aba correta para o widget correspondente na pilha do QStackedWidget
        target_tab = self.tabs[index]
        target_widget = self._tab_to_widget.get(target_tab)

        if target_widget:
            self.container.setCurrentWidget(target_widget)

        self.tab_changed.emit(index)