from PySide6 import QtWidgets, QtCore
from .tab_ui import WorkspaceTabWidget


class TabController(QtCore.QObject):
    tab_changed = QtCore.Signal(int)
    tab_closed = QtCore.Signal(int)

    def __init__(self, container: QtWidgets.QStackedWidget):
        super().__init__()
        self.container = container
        self.tabs: list[WorkspaceTabWidget] = []

        self.tab_bar_layout = QtWidgets.QHBoxLayout()
        self.tab_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_bar_layout.setSpacing(2)

    def add_tab(self, title: str, content_widget: QtWidgets.QWidget):
        tab = WorkspaceTabWidget(title)
        tab.close_requested.connect(lambda: self._handle_close(tab))

        tab.clicked.connect(lambda: self.set_active(self.tabs.index(tab)))

        self.tabs.append(tab)
        self.container.addWidget(content_widget)
        self.tab_bar_layout.addWidget(tab)

    def _handle_close(self, tab: WorkspaceTabWidget):
        index = self.tabs.index(tab)
        self.tabs.pop(index)

        # Remove o conteúdo do QStackedWidget
        widget_to_remove = self.container.widget(index)
        if widget_to_remove:
            self.container.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()

        self.tab_bar_layout.removeWidget(tab)
        tab.deleteLater()

        self.tab_closed.emit(index)

    def set_active(self, index: int):
        """Gerencia o estado visual de qual aba está ativa."""
        for i, tab in enumerate(self.tabs):
            tab.set_active(i == index)
        self.container.setCurrentIndex(index)