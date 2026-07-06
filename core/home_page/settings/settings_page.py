from PySide6 import QtWidgets, QtCore
from settings.general.tab_language import TabLanguage
from settings.general.tab_appearance import TabAppearance
from settings.general.tab_keyboard import TabKeyboard


from core.home_page.settings.viewer.tab_2d import Tab2DViewer
from core.home_page.settings.viewer.tab_3d import Tab3DViewer

class PaginaConfig(QtWidgets.QWidget):
    voltar_solicitado = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)

        # Menu Lateral (Tree)
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setFixedWidth(200)

        # Conteúdo (Stack)
        self.stack = QtWidgets.QStackedWidget()

        # Adição de Abas - Grupo General
        self._add_tab("General", "Language", TabLanguage())
        self._add_tab("General", "Appearance", TabAppearance())
        self._add_tab("General", "Keyboard Shortcuts", TabKeyboard())

        # Adição de Abas - Grupo Viewer (Novas)
        self._add_tab("Viewer", "2D Viewer", Tab2DViewer())
        self._add_tab("Viewer", "3D Viewer", Tab3DViewer())

        self.tree.expandAll()
        self.tree.currentItemChanged.connect(self._on_item_changed)

        main_layout.addWidget(self.tree)
        main_layout.addWidget(self.stack)

    def _add_tab(self, group_name, tab_name, widget):
        # Busca ou cria o grupo
        items = self.tree.findItems(group_name, QtCore.Qt.MatchExactly)
        if not items:
            parent = QtWidgets.QTreeWidgetItem(self.tree, [group_name])
        else:
            parent = items[0]

        child = QtWidgets.QTreeWidgetItem(parent, [tab_name])
        self.stack.addWidget(widget)

        # Mapeamento do item para o índice do widget
        child.setData(0, QtCore.Qt.UserRole, self.stack.count() - 1)

    def _on_item_changed(self, current, previous):
        if current and current.data(0, QtCore.Qt.UserRole) is not None:
            self.stack.setCurrentIndex(current.data(0, QtCore.Qt.UserRole))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    # Opcional: Aplique uma folha de estilo básica para ver o menu lateral destacado
    app.setStyleSheet("""
        QTreeWidget {
            border: none;
            background-color: #f0f0f0;
            padding-top: 10px;
        }
        QStackedWidget {
            border-left: 1px solid #ccc;
        }
    """)

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Configurações do Sistema")
    window.resize(800, 600)

    config_page = PaginaConfig()
    window.setCentralWidget(config_page)

    window.show()
    sys.exit(app.exec())