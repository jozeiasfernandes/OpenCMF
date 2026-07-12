from PySide6 import QtWidgets, QtCore
from typing import Optional
from core.scene.scene_manager import SceneManager
from core.scene.events.event_bus import EventBus


class BaseSidePanel(QtWidgets.QWidget):
    side_panel_name: str = "Painel Lateral Genérico"

    def __init__(
            self,
            scene_manager: Optional[SceneManager] = None,
            parent: Optional[QtWidgets.QWidget] = None
    ):
        super().__init__(parent)
        self.scene_manager = scene_manager

        # Acesso direto ao barramento de eventos através do manager
        self.event_bus: Optional[EventBus] = (
            self.scene_manager.events if self.scene_manager else None
        )

        # Configuração básica de layout que todos os painéis devem ter
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.setup_ui()

    def setup_ui(self) -> None:
        """
        Método a ser sobrescrito pelos painéis específicos.
        """
        pass

    @property
    def has_scene(self) -> bool:
        """Verifica se o painel possui uma cena conectada."""
        return self.scene_manager is not None