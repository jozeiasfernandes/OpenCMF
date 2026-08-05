from typing import Optional, TYPE_CHECKING
from PySide6 import QtWidgets, QtCore, QtGui

from core.components.bases.base_toolbar.base_toolbar import BaseToolbar
from core.components.bases.base_tool.tool_manager import ToolManager
from core.components.tools.add_point_registration_tool import AddPointRegistrationTool
from core.components.tools.select_tool import SelectTool

from settings.localization.translator import tr
from list_paths import ICONS_DIR
from core.scene.events.scene_events import RegistrationEvents

if TYPE_CHECKING:
    pass


class RegistrationToolbar(BaseToolbar):
    def __init__(self, app_context: "AppContext", parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(title="Registration", app_context=app_context, parent=parent)

    def get_icon(self, icon_name: str, fallback=QtWidgets.QStyle.StandardPixmap.SP_FileIcon) -> QtGui.QIcon:
        """Método helper da classe para carregar ícones com segurança."""
        path = ICONS_DIR / icon_name
        if path.exists():
            return QtGui.QIcon(str(path))
        return QtWidgets.QApplication.style().standardIcon(fallback)

    def setup_ui(self) -> None:
        """Configura a interface da toolbar de registro."""
        # 1. Registro de ferramentas (BaseToolbar gerencia o registro no ToolManager)
        self.register_tool(SelectTool())
        self.register_tool(AddPointRegistrationTool())

        self.add_separator()

        # 2. Botão de remover ponto
        self.add_action_button(
            text="",
            callback=self._on_delete_point,
            icon=self.get_icon("del_point.svg", QtWidgets.QStyle.StandardPixmap.SP_TrashIcon),
            tooltip=tr("toolbar_container.del_point", "Remover Último Ponto")
        )

        # 3. Botão de resetar vista
        self.add_action_button(
            text="",
            callback=self._on_reset_view,
            icon=self.get_icon("home.svg", QtWidgets.QStyle.StandardPixmap.SP_BrowserReload),
            tooltip=tr("toolbar_container.reset_view", "Resetar Vista")
        )

        self.add_separator()

        # 4. Slider de tamanho
        self.addWidget(QtWidgets.QLabel(tr("toolbar_container.point_size", " Tamanho: ")))
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(5, 50)
        self.slider.setFixedWidth(80)
        self.slider.setValue(20)
        self.slider.valueChanged.connect(self._on_point_size_changed)
        self.addWidget(self.slider)

    def _on_delete_point(self):
        """Remove o último marcador."""
        if self.scene_manager and hasattr(self.scene_manager, 'events'):
            self.scene_manager.events.emit(RegistrationEvents.REGISTRATION_DELETE_LAST_MARKER)

    def _on_reset_view(self):
        """Reseta a visualização."""
        if self.scene_manager and hasattr(self.scene_manager, 'events'):
            self.scene_manager.events.emit(RegistrationEvents.REGISTRATION_RESET_LAYOUT)

    def _on_point_size_changed(self, value: int):
        """Altera o tamanho dos pontos."""
        if self.scene_manager and hasattr(self.scene_manager, 'events'):
            self.scene_manager.events.emit(
                RegistrationEvents.REGISTRATION_POINT_SIZE_CHANGED,
                size=value / 10.0
            )


if __name__ == "__main__":
    import sys
    from core.components.bases.base_toolbar import AppContext

    app_context = AppContext(
        tool_manager=ToolManager(),
        scene_manager=None,
        settings=None
    )

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    main_window = QtWidgets.QMainWindow()

    toolbar = RegistrationToolbar(
        app_context=app_context,
        parent=main_window
    )

    main_window.addToolBar(toolbar)
    main_window.setWindowTitle("Registration Toolbar")
    main_window.resize(600, 400)
    main_window.show()

    sys.exit(app.exec())