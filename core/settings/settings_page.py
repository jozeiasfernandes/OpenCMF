from PySide6 import QtWidgets, QtCore

from core.settings.tabs.general.tab_language import TabLanguage
from core.settings.tabs.general.tab_appearance import TabAppearance
from core.settings.tabs.general.tab_keyboard import TabKeyboard
from core.settings.tabs.viewer.tab_2d import Tab2DViewer
from core.settings.tabs.viewer.tab_3d import Tab3DViewer
from core.settings.tabs.workspace.tab_toolbar import TabToolbar
from core.settings.tabs.workspace.tab_side_panel import TabSidePanel
from core import tr


class PaginaConfig(QtWidgets.QWidget):
    voltar_solicitado = QtCore.Signal()
    tema_alterado = QtCore.Signal(str)

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self._setup_ui()
        self._conectar_sinais_internos()

    def _setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        content_layout = QtWidgets.QHBoxLayout()

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setFixedWidth(200)

        self.stack = QtWidgets.QStackedWidget()
        self._adicionar_abas()

        self.btn_voltar = QtWidgets.QPushButton(tr("Exit"))
        self.btn_voltar.clicked.connect(self.voltar_solicitado.emit)

        self.tree.expandAll()
        self.tree.currentItemChanged.connect(self._navegar_entre_abas)

        content_layout.addWidget(self.tree)
        content_layout.addWidget(self.stack)
        main_layout.addLayout(content_layout)
        main_layout.addWidget(self.btn_voltar)

    def _adicionar_abas(self):
        self._adicionar_aba_ao_tree(tr("configs.general"), tr("configs.language"), TabLanguage())
        self._adicionar_aba_ao_tree(tr("configs.general"), tr("configs.appearance"), TabAppearance())
        self._adicionar_aba_ao_tree(tr("configs.general"), tr("configs.keyboard_shortcuts"), TabKeyboard())

        self._adicionar_aba_ao_tree(tr("configs.viewer"), tr("configs.2d_viewer"), Tab2DViewer())
        self._adicionar_aba_ao_tree(tr("configs.viewer"), tr("configs.3d_viewer"), Tab3DViewer())

        self._adicionar_aba_ao_tree(tr("configs.workspace", "Workspace"), tr("configs.toolbar", "Toolbar"), TabToolbar())
        self._adicionar_aba_ao_tree(tr("configs.workspace", "Workspace"), tr("configs.side_panel", "Side Panel"), TabSidePanel())

    def _adicionar_aba_ao_tree(self, grupo, nome, widget):
        items = self.tree.findItems(grupo, QtCore.Qt.MatchExactly)
        parent = items[0] if items else QtWidgets.QTreeWidgetItem(self.tree, [grupo])

        child = QtWidgets.QTreeWidgetItem(parent, [nome])
        self.stack.addWidget(widget)
        child.setData(0, QtCore.Qt.UserRole, self.stack.count() - 1)

    def _navegar_entre_abas(self, current):
        if current and current.data(0, QtCore.Qt.UserRole) is not None:
            self.stack.setCurrentIndex(current.data(0, QtCore.Qt.UserRole))

    def _conectar_sinais_internos(self):
        for i in range(self.stack.count()):
            widget = self.stack.widget(i)
            if isinstance(widget, TabAppearance):
                widget.tema_alterado.connect(self.tema_alterado.emit)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    window = QtWidgets.QMainWindow()
    window.setCentralWidget(PaginaConfig())
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())