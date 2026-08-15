# Lógica de controle das abas
# Adicionar, remover, ordenar, ativar e sincronizar com o QStackedWidget.

from PySide6 import QtWidgets, QtCore
from core.workspace.modules.tabs.tab_widget import WorkspaceTabWidget


class TabController(QtCore.QObject):
    tab_changed = QtCore.Signal(int)
    tab_closed = QtCore.Signal(int)

    def __init__(self, container: QtWidgets.QStackedWidget):
        super().__init__()
        self.container = container
        self.tabs: list[WorkspaceTabWidget] = []
        self._tab_to_widget: dict[WorkspaceTabWidget, QtWidgets.QWidget] = {}

        self.tab_bar_layout = QtWidgets.QHBoxLayout()
        self.tab_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_bar_layout.setSpacing(2)
        self.tab_bar_layout.addStretch()  # Mantém as abas alinhadas à esquerda

    def add_tab(self, title: str, content_widget: QtWidgets.QWidget):
        tab = WorkspaceTabWidget(title)

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

    def clear_tabs(self):
        """Remove e deleta todas as abas e widgets associados de forma segura."""
        # Remove os widgets associados do container
        for tab, widget in list(self._tab_to_widget.items()):
            try:
                _ = widget.metaObject()
                self.container.removeWidget(widget)
                widget.deleteLater()
            except RuntimeError:
                pass

        # Remove as abas visuais do layout e deleta
        for tab in list(self.tabs):
            try:
                _ = tab.metaObject()
                self.tab_bar_layout.removeWidget(tab)
                tab.deleteLater()
            except RuntimeError:
                pass

        self.tabs.clear()
        self._tab_to_widget.clear()

    def _on_tab_clicked(self, tab: WorkspaceTabWidget):
        if tab in self.tabs:
            index = self.tabs.index(tab)
            self.set_active(index)

    def _handle_close(self, tab: WorkspaceTabWidget):
        if tab not in self.tabs:
            return

        index = self.tabs.index(tab)
        widget = self._tab_to_widget.pop(tab, None)
        if tab in self.tabs:
            self.tabs.remove(tab)

        # Remove do Container e limpa da pilha de forma segura
        if widget is not None:
            try:
                _ = widget.metaObject()
                self.container.removeWidget(widget)
                widget.deleteLater()
            except RuntimeError:
                pass

        # Remove visualmente
        try:
            _ = tab.metaObject()
            self.tab_bar_layout.removeWidget(tab)
            tab.deleteLater()
        except RuntimeError:
            pass

        self.tab_closed.emit(index)

        # Ajusta a aba ativa para a anterior ou próxima
        if self.tabs:
            new_index = max(0, index - 1)
            self.set_active(new_index)

    def set_active(self, index: int):
        if not (0 <= index < len(self.tabs)):
            return

        for i, tab in enumerate(self.tabs):
            try:
                _ = tab.metaObject()
                tab.set_active(i == index)
            except RuntimeError:
                pass

        # Mapeia a aba correta para o widget correspondente na pilha do QStackedWidget
        target_tab = self.tabs[index]
        target_widget = self._tab_to_widget.get(target_tab)

        if target_widget is not None:
            try:
                # Valida se o objeto C++ subjacente ainda existe na memória
                _ = target_widget.metaObject()
                self.container.setCurrentWidget(target_widget)
            except RuntimeError:
                # O widget foi deletado do C++; evitamos o crash e ignoramos a chamada
                pass

        self.tab_changed.emit(index)