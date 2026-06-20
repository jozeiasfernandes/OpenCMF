import sys
from typing import TYPE_CHECKING
from PySide6 import QtWidgets, QtCore
from typing import TYPE_CHECKING, Optional

# Importações necessárias para os tipos
from core.components.tools.base.base_tool import InteractionContext
from core.components.tools.base.base_toolbar_handler import BaseToolbarHandler
from core.components.tools.add_point_registration_tool import AddPointRegistrationTool
from core.components.tools.del_point_registration_tool import DelPointRegistrationTool
from core.components.tools.move_tool import MoveTool
from core.localization.translator import get_base_dir, tr

from core.scene.events.scene_events import (
    REGISTRATION_DELETE_LAST_MARKER,
    REGISTRATION_IMPORT_REQUESTED,
    REGISTRATION_POINT_SIZE_CHANGED,
    REGISTRATION_RESET_LAYOUT,
    INTERACTION_MODE_CHANGED
)

if TYPE_CHECKING:
    from core.scene.scene_manager import SceneManager

if TYPE_CHECKING:
    pass

class TestToolbar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("test_toolbar_widget")
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        # Layout principal
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Criamos o widget de Toolbar
        self.toolbar_widget = QtWidgets.QToolBar(self)
        self.toolbar_widget.setObjectName("registration_toolbar")
        self.toolbar_widget.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        layout.addWidget(self.toolbar_widget)

        # ==================== ESTILO VERDE (CORRIGIDO) ====================
        self.setStyleSheet("""
            /* Fundo do container */
            #test_toolbar_widget {
                background-color: #2e6b28;
            }

            /* Estilo principal da Toolbar */
            QToolBar#registration_toolbar {
                background-color: #2e6b28;
                border-bottom: 2px solid #1f4a1c;
                padding: 3px;
                spacing: 4px;
            }

            QToolBar#registration_toolbar::separator {
                background: #1f4a1c;
                width: 1px;
                margin: 4px 6px;
            }

            /* Botões */
            QToolButton {
                background: transparent;
                border: none;
                padding: 6px;
                border-radius: 4px;
            }

            QToolButton:hover {
                background: #3a8b34;
            }

            QToolButton:pressed,
            QToolButton:checked {
                background: #25621f;
                border: 1px solid #5cb14f;
            }
        """)



class RegistrationToolbarHandler(QtCore.QObject):
    def __init__(self, toolbar: QtWidgets.QToolBar, scene_manager: Optional["SceneManager"] = None):
        super().__init__()
        self.toolbar = toolbar
        self._scene_manager = scene_manager
        self._setup_ui()

    def _setup_ui(self):
        self.toolbar.setIconSize(QtCore.QSize(24, 24))



class Component(QtWidgets.QToolBar):
    def __init__(self, modulo=None, scene_manager: Optional["SceneManager"] = None):
        super().__init__()
        self.modulo = modulo
        self.setWindowTitle(tr("toolbar.registration.title", "Alinhamento de Objetos"))
        self.setObjectName("registration_toolbar")
        self.handler = RegistrationToolbarHandler(self, scene_manager=scene_manager)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    win = QtWidgets.QMainWindow()
    win.setWindowTitle("Teste de Carregamento de Tools")
    win.resize(900, 600)

    # 1. Setup da Toolbar
    toolbar = TestToolbar()

    # 2. Setup do contexto (Mock)
    # Certifique-se de que o BaseTool espera esses argumentos no __init__
    class MockContext(InteractionContext):
        def __init__(self):
            # Passando None para os argumentos obrigatórios da dataclass
            super().__init__(renderer=None, interactor=None, window=win)

    context = MockContext()

    # 3. Inicialização do Handler
    handler = BaseToolbarHandler(toolbar.toolbar_widget, context)

    # 4. Criação da lista de ferramentas
    minhas_ferramentas = [
        AddPointRegistrationTool(),
        DelPointRegistrationTool(),
        MoveTool(),
    ]

    # 5. Carregamento automático
    handler.load_tools(minhas_ferramentas)

    # --- Ajuste visual ---
    container = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(container)
    layout.addWidget(toolbar)
    layout.addStretch()
    win.setCentralWidget(container)

    win.show()
    sys.exit(app.exec())