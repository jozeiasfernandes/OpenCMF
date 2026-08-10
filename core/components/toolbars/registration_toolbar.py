from typing import Optional, TYPE_CHECKING
from PySide6 import QtWidgets, QtCore, QtGui

from core.components.bases.base_toolbar.base_toolbar import BaseToolbar
from core.components.bases.base_tool.tool_manager import ToolManager
from core.components.tools.registration.add_point_registration_tool import AddPointRegistrationTool
from core.components.tools.scene.select_tool import SelectTool
from core.components.tools.imports.import_tool import ImportTool

from core.settings.localization.translator import tr
from core.settings.paths.list_paths import ICONS_DIR
from application.scene.events.scene_events import RegistrationEvents

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

        # 1. Import objects (Armazenado em self.import_tool para evitar coleta de lixo pelo Python)
        self.import_tool = ImportTool(context=self.app)

        # Utiliza o método create_action da tool (ou add_action_button referenciando self.import_tool)
        if hasattr(self.import_tool, "create_action"):
            self.addAction(self.import_tool.create_action(self))
        else:
            self.add_action_button(
                text="",
                callback=self.import_tool.execute_import,
                icon=self.import_tool.get_qicon() if hasattr(self.import_tool, "get_qicon") else self.get_icon(
                    "import.svg", QtWidgets.QStyle.StandardPixmap.SP_FileIcon),
                tooltip=getattr(self.import_tool, "tool_tip", "Importar Objetos")
            )

        # 2. Registro de ferramentas de manipulação de cena (BaseToolbar gerencia o registro no ToolManager)
        self.register_tool(SelectTool())
        self.register_tool(AddPointRegistrationTool())

        self.add_separator()

        # 3. Botão de remover ponto
        self.add_action_button(
            text="",
            callback=self._on_delete_point,
            icon=self.get_icon("del_point.svg", QtWidgets.QStyle.StandardPixmap.SP_TrashIcon),
            tooltip=tr("toolbar_container.del_point", "Remover Último Ponto")
        )

        # 4. Botão de resetar vista
        self.add_action_button(
            text="",
            callback=self._on_reset_view,
            icon=self.get_icon("home.svg", QtWidgets.QStyle.StandardPixmap.SP_BrowserReload),
            tooltip=tr("toolbar_container.reset_view", "Resetar Vista")
        )

        self.add_separator()

        # 5. Slider de tamanho
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
            self.scene_manager.events.emit(RegistrationEvents.DELETE_LAST_MARKER)

    def _on_reset_view(self):
        """Reseta a visualização."""
        if self.scene_manager and hasattr(self.scene_manager, 'events'):
            self.scene_manager.events.emit(RegistrationEvents.RESET_LAYOUT)

    def _on_point_size_changed(self, value: int):
        """Altera o tamanho dos pontos."""
        if self.scene_manager and hasattr(self.scene_manager, 'events'):
            self.scene_manager.events.emit(
                RegistrationEvents.POINT_SIZE_CHANGED,
                size=value / 10.0
            )


if __name__ == "__main__":
    import sys
    from core.components.bases.base_component import AppContext

    class MockEventBus:
        def emit(self, event, **kwargs):
            print(f"[MockEventBus] Evento emitido: {event} | Payload: {kwargs}")

    class MockSceneManager:
        def __init__(self):
            self.events = MockEventBus()

    app_context = AppContext(
        tool_manager=ToolManager(),
        scene_manager=MockSceneManager(),
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