from typing import Optional, Any, TYPE_CHECKING
from PySide6 import QtWidgets, QtCore, QtGui
from core.components.bases.base_toolbar import BaseToolbar, ToolData
from core.components.bases.base_tool.tool_manager import ToolManager
from core.localization.translator import get_base_dir, tr
from core.scene.events.scene_events import SceneEvents, RegistrationEvents

if TYPE_CHECKING:
    from core.scene.scene_manager import SceneManager


def get_icon(icon_name: str, fallback=QtWidgets.QStyle.StandardPixmap.SP_FileIcon) -> QtGui.QIcon:
    path = get_base_dir() / "appearance" / "icons" / icon_name
    if path.exists():
        return QtGui.QIcon(str(path))
    return QtWidgets.QApplication.style().standardIcon(fallback)


class RegistrationToolbar(BaseToolbar):
    """Toolbar para ferramentas de registro/calibração."""

    def __init__(self, tool_manager: ToolManager,
                 scene_manager: Optional["SceneManager"] = None,
                 parent: Optional[QtWidgets.QWidget] = None):

        # ✅ CHAMADA CORRETA: (context, title, parent)
        super().__init__(context=scene_manager, title="Registration", parent=parent)

        # Guardar referências
        self._tool_manager = tool_manager
        self._scene_manager = scene_manager

        self.setObjectName("registration_toolbar")
        self.setIconSize(QtCore.QSize(24, 24))

        # Setup da UI
        self.setup_ui()

    @property
    def scene_manager(self):
        return self._scene_manager

    @property
    def tool_manager(self):
        return self._tool_manager

    def setup_ui(self):
        """Configura os botões da toolbar."""

        # Botão de remover ponto
        tool_data_delete = ToolData(
            name="delete_point",
            display_name="",
            icon_path=None,
            tool_tip=tr("toolbar_container.del_point", "Remover Último Ponto"),
            callback=self._on_delete_point,
            is_checkable=False
        )
        self.add_tool_button(
            tool_data_delete,
            icon=get_icon("del_point.svg", QtWidgets.QStyle.StandardPixmap.SP_TrashIcon)
        )

        # Botão de resetar vista
        tool_data_reset = ToolData(
            name="reset_view",
            display_name="",
            icon_path=None,
            tool_tip=tr("toolbar_container.reset_view", "Resetar Vista"),
            callback=self._on_reset_view,
            is_checkable=False
        )
        self.add_tool_button(
            tool_data_reset,
            icon=get_icon("home.svg", QtWidgets.QStyle.StandardPixmap.SP_BrowserReload)
        )

        self.addSeparator()

        # Label de tamanho
        self.addWidget(QtWidgets.QLabel(tr("toolbar_container.point_size", " Tamanho: ")))

        # Slider de tamanho
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

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    main_window = QtWidgets.QMainWindow()

    # Criar tool_manager e toolbar
    tool_manager = ToolManager(context=main_window)
    toolbar = RegistrationToolbar(
        tool_manager=tool_manager,
        scene_manager=None,
        parent=main_window
    )

    main_window.addToolBar(toolbar)
    main_window.setWindowTitle("Registration Toolbar")
    main_window.resize(600, 400)
    main_window.show()

    sys.exit(app.exec())