from PySide6 import QtWidgets, QtCore


class ToolboxesManager(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout_principal = QtWidgets.QHBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.hide()

        self.stack.setContentsMargins(0, 0, 0, 0)

        self.stack.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Expanding
        )

        self.tab_bar = QtWidgets.QTabBar()

        self.tab_bar.setShape(
            QtWidgets.QTabBar.RoundedEast
        )

        self.tab_bar.setCursor(
            QtCore.Qt.PointingHandCursor
        )

        self.tab_bar.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Expanding
        )

        self.tab_bar.tabBarClicked.connect(
            self._gerenciar_clique
        )

        self.layout_principal.addWidget(self.stack)
        self.layout_principal.addWidget(self.tab_bar)

    def adicionar_widget(
        self,
        titulo: str,
        widget: QtWidgets.QWidget
    ):
        widget.setContentsMargins(0, 0, 0, 0)

        widget.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Expanding
        )

        idx = self.stack.addWidget(widget)

        self.tab_bar.addTab(titulo)

        return idx

    def limpar(self):
        while self.stack.count() > 0:
            w = self.stack.widget(0)

            self.stack.removeWidget(w)

            w.deleteLater()

        self.tab_bar.clear()

        self.stack.hide()

    def renomear_tab(
        self,
        index: int,
        novo_titulo: str
    ) -> bool:

        if 0 <= index < self.tab_bar.count():
            self.tab_bar.setTabText(
                index,
                novo_titulo
            )

            return True

        return False

    def obter_titulo_tab(self, index: int) -> str:
        if 0 <= index < self.tab_bar.count():
            return self.tab_bar.tabText(index)

        return ""

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