import sys
from typing import TYPE_CHECKING, Optional, List
from PySide6 import QtWidgets, QtCore, QtGui

# Importações necessárias para os tipos
from core.tools.base.base_tool import BaseTool, InteractionContext
from core.tools.base.base_toolbar_handler import BaseToolbarHandler
from core.tools.add_point_registration_tool import AddPointRegistrationTool
from core.tools.del_point_registration_tool import DelPointRegistrationTool
from core.tools.move_tool import MoveTool

if TYPE_CHECKING:
    from core.scene.scene_manager import SceneManager

class TestToolbar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("test_toolbar_widget")
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self.setStyleSheet("""
            #test_toolbar_widget {
                background-color: #3c8033;
                border-bottom: 1px solid #000;
            }
            QToolButton {
                background: transparent;
                border: none;
                padding: 5px;
            }
            QToolButton:hover {
                background: #458e3a;
                border-radius: 3px;
            }
        """)

        # Layout principal
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) # Margem zero para a toolbar ocupar o espaço todo
        layout.setSpacing(0)

        # Criamos o widget de Toolbar
        self.toolbar_widget = QtWidgets.QToolBar(self)
        # Importante: Toolbar dentro de QWidget funciona melhor com estilo de ícone/texto ajustado
        self.toolbar_widget.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        layout.addWidget(self.toolbar_widget)

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