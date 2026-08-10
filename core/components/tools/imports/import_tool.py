from __future__ import annotations
import logging
from typing import Optional, Any
from PySide6 import QtWidgets, QtCore, QtGui

# Components
from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory, InteractionContext

# Settings
from core.settings.localization.translator import tr
from core.settings.icons_manager.icon_manager import IconManager

# Import Window Integration
from core.application.imports.import_window.import_window import ImportWindow

logger = logging.getLogger(__name__)


class ImportTool(BaseTool):
    """
    Ferramenta responsável por abrir a janela avançada de importação (ImportWindow)
    e injetar os itens na cena através do contexto centralizado.
    """
    name = "import_tool"
    category = ToolCategory.OBJECTS
    icon = "add_box"

    def __init__(self, context: Optional[Any] = None, parent: Optional[QtCore.QObject] = None):
        super().__init__()
        # Aceita tanto app_context quanto InteractionContext direto
        self._app_context = context
        self._parent = parent
        self._import_window: Optional[ImportWindow] = None

    @property
    def display_name(self) -> str:
        return tr("tools.import.display_name", "Importar")

    @property
    def tool_tip(self) -> str:
        return tr("tools.import.tooltip", "Abrir gerenciador de importação de arquivos e objetos 3D")

    def create_button(self, callback=None) -> QtWidgets.QToolButton:
        """Cria o botão próprio da tool para uso isolado ou customizado."""
        btn = QtWidgets.QToolButton()
        btn.setText(self.display_name)
        btn.setToolTip(self.tool_tip)
        btn.setIcon(self.get_qicon())
        btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        btn.setCheckable(False)
        # Se um callback customizado for passado, usa ele; senão, usa o execute_import interno
        btn.clicked.connect(callback if callback else self.execute_import)
        return btn

    def execute_import(self) -> None:
        """Método unificado de execução disparado por qualquer botão ou toolbar."""
        print("[DEBUG] ImportTool.execute_import acionado com sucesso!")
        logger.info("execute_import chamado!")

        try:
            # 1. Determina a janela pai de forma segura
            parent_window = None
            if self._app_context and hasattr(self._app_context, "window") and self._app_context.window:
                parent_window = self._app_context.window
            elif self.context and hasattr(self.context, "window") and self.context.window:
                parent_window = self.context.window
            else:
                parent_window = QtWidgets.QApplication.activeWindow()

            # 2. Valida se a janela C++ anterior ainda está viva
            if self._import_window is not None:
                try:
                    _ = self._import_window.isHidden()
                except RuntimeError:
                    self._import_window = None

            # 3. Resolve o gerenciador de cena de qualquer fonte possível
            if self._import_window is None:
                scene_mgr = None
                sources = [
                    self._app_context,
                    self.context,
                    getattr(self, "scene_manager", None),
                    getattr(self, "scene", None)
                ]

                for source in sources:
                    if source:
                        if hasattr(source, "scene_manager") and source.scene_manager:
                            scene_mgr = source.scene_manager
                            break
                        elif hasattr(source, "scene") and source.scene:
                            scene_mgr = source.scene
                            break
                        elif type(source).__name__ in ("SceneManager", "MockSceneManager"):
                            scene_mgr = source
                            break

                self._import_window = ImportWindow(scene_mgr, parent=parent_window)
                self._import_window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

            self._import_window.show()
            self._import_window.raise_()
            self._import_window.activateWindow()

            logger.info("Janela ImportWindow exibida com sucesso.")

        except Exception as e:
            print(f"[ERRO CRÍTICO] Falha ao abrir ImportWindow: {e}")
            logger.error(f"FALHA CRÍTICA ao abrir ImportWindow: {e}", exc_info=True)
            self._import_window = None

    def get_qicon(self) -> QtGui.QIcon:
        return IconManager.get_instance().get_icon(self.icon, size=24)

    def activate(self, context: InteractionContext) -> None:
        """Mantém compatibilidade caso o sistema tente ativá-la via ToolManager."""
        super().activate(context)
        self.execute_import()
        self.deactivate()

    def create_action(self, parent: QtWidgets.QWidget) -> QtGui.QAction:
        """Cria e retorna uma QAction pronta para ser adicionada a toolbars."""
        action = QtGui.QAction(self.get_qicon(), self.display_name, parent)
        action.setToolTip(self.tool_tip)
        action.triggered.connect(self.execute_import)
        return action


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    # Configura o logging básico para exibir mensagens no console durante o teste isolado
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)

    tool = ImportTool()
    button = tool.create_button(None)
    button.setWindowTitle("Teste ImportTool")
    button.resize(200, 100)
    button.show()

    sys.exit(app.exec())