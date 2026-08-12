from __future__ import annotations

from typing import Optional
from PySide6 import QtCore, QtWidgets

# Localization
from core.settings.localization.translator import tr

# Tabs
from core.settings.settings_page_tabs.general.tab_appearance_settings import TabAppearance
from core.settings.settings_page_tabs.general.tab_keyboard_settings import TabKeyboard
from core.settings.settings_page_tabs.general.tab_language_settings import TabLanguage

from core.settings.settings_page_tabs.viewer.tab_2d_settings import Tab2DViewer
from core.settings.settings_page_tabs.viewer.tab_3d_settings import Tab3DViewer

from core.settings.settings_page_tabs.workspace.tab_side_panel_settings import TabSidePanel
from core.settings.settings_page_tabs.workspace.tab_toolbar_settings import TabToolbar


class PaginaConfig(QtWidgets.QWidget):
    voltar_solicitado = QtCore.Signal()
    tema_alterado = QtCore.Signal(str)

    def __init__(
        self,
        workspace_manager: Optional[QtWidgets.QWidget] = None,
        parent: QtWidgets.QWidget = None,
    ):
        super().__init__(parent)
        self.workspace_manager = workspace_manager
        self._setup_ui()
        self._connect_internal_signals()
        self.select_first_tab()

    def _setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        content_layout = QtWidgets.QHBoxLayout()

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setFixedWidth(200)
        self.tree.currentItemChanged.connect(self.Navigate_between_tabs)

        self.stack = QtWidgets.QStackedWidget()
        self._add_tabs()

        # Chamado após adicionar as abas para garantir que os grupos fiquem abertos
        self.tree.expandAll()

        self.btn_voltar = QtWidgets.QPushButton(tr("common.back", "Voltar"))
        self.btn_voltar.clicked.connect(self.voltar_solicitado.emit)

        content_layout.addWidget(self.tree)
        content_layout.addWidget(self.stack)
        main_layout.addLayout(content_layout)
        main_layout.addWidget(self.btn_voltar)

    # =========================================================================
    # TAB MANAGEMENT
    # =========================================================================
    def _add_tabs(self):
        self._add_tab_to_tree(
            tr("configs.general"), tr("configs.language"), TabLanguage())
        self._add_tab_to_tree(
            tr("configs.general"), tr("configs.appearance"), TabAppearance())
        self._add_tab_to_tree(
            tr("configs.general"),
            tr("configs.keyboard_shortcuts"),
            TabKeyboard(),
        )

        self._add_tab_to_tree(tr("configs.volume_viewer"), tr("configs.2d_viewer"), Tab2DViewer())
        self._add_tab_to_tree(tr("configs.volume_viewer"), tr("configs.3d_viewer"), Tab3DViewer())
        self._add_tab_to_tree(
            tr("configs.workspace", "Workspace"),
            tr("configs.toolbar", "Toolbar"),
            TabToolbar(),)
        self._add_tab_to_tree(
            tr("configs.workspace", "Workspace"),
            tr("configs.side_panel", "Side Panel"),
            TabSidePanel(),)

    def _add_tab_to_tree(self, grupo, nome, widget):
        items = self.tree.findItems(grupo, QtCore.Qt.MatchExactly)
        parent = (
            items[0] if items else QtWidgets.QTreeWidgetItem(self.tree, [grupo])
        )

        child = QtWidgets.QTreeWidgetItem(parent, [nome])
        self.stack.addWidget(widget)
        child.setData(0, QtCore.Qt.UserRole, self.stack.count() - 1)

    # =========================================================================
    # NAVIGATION & SIGNALS
    # =========================================================================
    def select_first_tab(self):
        """Garante que a primeira aba filha da árvore seja selecionada ao abrir."""
        if self.tree.topLevelItemCount() > 0:
            parent = self.tree.topLevelItem(0)
            if parent.childCount() > 0:
                first_child = parent.child(0)
                self.tree.setCurrentItem(first_child)

    def Navigate_between_tabs(self, current):
        if current and current.data(0, QtCore.Qt.UserRole) is not None:
            self.stack.setCurrentIndex(current.data(0, QtCore.Qt.UserRole))

    def _connect_internal_signals(self):
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