from __future__ import annotations
import logging
from typing import Optional, Any
from PySide6 import QtWidgets, QtCore

# Components
from core.components.bases.base_component import BaseComponent
from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory, InteractionContext

# Settings
from core.settings.localization.translator import tr

# Icons
from core.settings.icons_manager.icon_manager import IconManager
from core.settings.paths.list_paths import ICONS_DIR

# Import Window Integration
from core.application.imports.import_window.import_window import ImportWindow

logger = logging.getLogger(__name__)


class ImportTool(BaseTool, BaseComponent):
    """
    Ferramenta responsável por abrir a janela avançada de importação (ImportWindow)
    e injetar os itens na cena através do contexto centralizado.
    """
    name = "import_tool"
    category = ToolCategory.OBJECTS
    icon = "add_box"

    def __init__(self, context: Optional[Any] = None, parent: Optional[QtCore.QObject] = None):
        # Ignora a validação estrita padrão do BaseComponent se o contexto for parcial (como na toolbar de teste)
        BaseComponent.__init__(self, context=context, parent=parent)
        BaseTool.__init__(self)
        self.import_window: Optional[ImportWindow] = None

    @property
    def display_name(self) -> str:
        return tr("tools.import.display_name", "Importar")

    @property
    def tool_tip(self) -> str:
        return tr("tools.import.tooltip", "Abrir gerenciador de importação de arquivos e objetos 3D")

    def set_context(self, context: Any) -> None:
        """Sobrescreve set_context para evitar crash caso a toolbar receba um AppContext incompleto nos testes."""
        target_context = self._resolve_context(context)
        self._context = context

    @BaseComponent.context.setter
    def context(self, value: Any) -> None:
        """Permite que o BaseComponent defina o contexto sem conflito com a propriedade de BaseTool."""
        self.set_context(value)

    def get_qicon(self):
        """Utiliza o IconManager centralizado para recuperar o ícone SVG com suporte a temas."""
        icon_manager = IconManager.get_instance()
        return icon_manager.get_icon(self.icon, size=24)

    def create_button(self, callback) -> QtWidgets.QToolButton:
        btn = QtWidgets.QToolButton()
        btn.setText(self.display_name)
        btn.setToolTip(self.tool_tip)
        btn.setIcon(self.get_qicon())
        btn.setCheckable(False)
        btn.clicked.connect(self.execute_import)
        return btn

    def activate(self, context: InteractionContext) -> None:
        super().activate(context)
        self.execute_import()
        self.deactivate()

    def execute_import(self) -> None:
        """Abre a ImportWindow garantindo gerenciamento de instâncias e repasse do scene_manager."""
        # Evita múltiplas instâncias da janela de importação abertas simultaneamente
        if not self.import_window or not self.import_window.isVisible():
            scene_mgr = getattr(self, "scene_manager", None)
            self.import_window = ImportWindow(scene_manager=scene_mgr)

        # Exibe e traz a janela para o foco do usuário
        self.import_window.show()
        self.import_window.raise_()
        self.import_window.activateWindow()

        logger.info("Janela avançada de importação (ImportWindow) aberta com sucesso.")

    def setup_ui(self) -> None:
        pass

    def get_ui(self) -> Any:
        return None