from pathlib import Path
from PySide6 import QtWidgets, QtCore


class SidePanelManagerLoaders(QtWidgets.QWidget):
    """Gerencia componentes laterais carregados dinamicamente via abas e QStackedWidget."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout_principal = QtWidgets.QHBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.hide()
        self.stack.setContentsMargins(0, 0, 0, 0)
        self.stack.setMinimumWidth(0)
        self.stack.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )

        self.tab_bar = QtWidgets.QTabBar()
        self.tab_bar.setShape(QtWidgets.QTabBar.RoundedEast)
        self.tab_bar.setCursor(QtCore.Qt.PointingHandCursor)
        self.tab_bar.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Expanding
        )
        self.tab_bar.tabBarClicked.connect(self._gerenciar_clique)

        self.layout_principal.addWidget(self.stack)
        self.layout_principal.addWidget(self.tab_bar)

    def add_panel(self, titulo: str, widget: QtWidgets.QWidget):
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred
        )
        idx = self.stack.addWidget(widget)
        self.tab_bar.addTab(titulo)

        # Se for o primeiro painel, opcionalmente podemos exibi-lo ou manter oculto conforme o design da aplicação.
        # Caso queira que ele exiba automaticamente ao ser adicionado:
        if self.stack.count() == 1:
            self.stack.show()
            self.stack.setCurrentIndex(idx)
            self.tab_bar.setCurrentIndex(idx)

        return idx

    def limpar(self):
        while self.stack.count() > 0:
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.deleteLater()

        while self.tab_bar.count() > 0:
            self.tab_bar.removeTab(0)

        self.stack.hide()
        self.tab_bar.setCurrentIndex(-1)

    def renomear_tab(self, index: int, novo_titulo: str) -> bool:
        if 0 <= index < self.tab_bar.count():
            self.tab_bar.setTabText(index, novo_titulo)
            return True
        return False

    def obter_titulo_tab(self, index: int) -> str:
        if 0 <= index < self.tab_bar.count():
            return self.tab_bar.tabText(index)
        return ""

    def remover_widget_por_caminho(self, caminho):
        for i in range(self.stack.count()):
            w = self.stack.widget(i)
            mod_path = w.property("__module_path__")
            if mod_path and Path(mod_path) == Path(caminho):
                self.stack.removeWidget(w)
                self.tab_bar.removeTab(i)
                w.deleteLater()
                break

        if self.stack.count() == 0:
            self.stack.hide()
            self.tab_bar.setCurrentIndex(-1)
        else:
            current = self.stack.currentIndex()
            self.tab_bar.setCurrentIndex(current if current < self.stack.count() else self.stack.count() - 1)

    def _gerenciar_clique(self, index: int):
        if (
                not self.stack.isHidden()
                and self.tab_bar.currentIndex() == index
        ):
            self.stack.hide()
            self.tab_bar.setCurrentIndex(-1)
        else:
            self.stack.show()
            self.stack.setCurrentIndex(index)
            self.tab_bar.setCurrentIndex(index)