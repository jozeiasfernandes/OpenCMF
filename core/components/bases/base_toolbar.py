from typing import Optional, Callable, Any, Protocol, TYPE_CHECKING
from dataclasses import dataclass
from PySide6 import QtWidgets, QtCore, QtGui

if TYPE_CHECKING:
    from core.components.bases.base_tool.tool_manager import ToolManager
    from core.scene.scene_manager import SceneManager
    from core.components.bases.base_tool.base_tool import BaseTool


class Settings(Protocol):
    """Protocolo para configurações, permitindo diferentes implementações."""

    def get(self, key: str, default: Any = None) -> Any: ...

    def set(self, key: str, value: Any) -> None: ...


class AppContext:
    """
    Contêiner central de dependências para componentes da interface.
    Facilita a injeção de dependências e evita acoplamento rígido.
    """

    def __init__(self,
                 tool_manager: 'ToolManager',
                 scene_manager: 'SceneManager',
                 settings: Settings):
        self.tool_manager = tool_manager
        self.scene_manager = scene_manager
        self.settings = settings


@dataclass
class ToolData:
    """Dados para criação de botões de ferramentas na toolbar."""
    name: str
    display_name: str
    icon_path: Optional[str]
    tool_tip: str
    callback: Callable
    is_checkable: bool = True


class BaseToolbar(QtWidgets.QToolBar):
    """
    Classe base para toolbars com injeção de dependência centralizada via AppContext.

    Fornece:
    - Acesso centralizado a dependências via self.app
    - Propriedades de conveniência para tool_manager, scene_manager e settings
    - Métodos para adição de ferramentas e botões
    - Ciclo de vida com initialize() e dispose()
    """

    # Sinal emitido quando uma ferramenta é ativada/desativada
    tool_toggled = QtCore.Signal(object, bool)  # tool, checked

    def __init__(self,
                 title: str,
                 app_context: AppContext,
                 parent: Optional[QtWidgets.QWidget] = None,
                 is_movable: bool = True):

        super().__init__(title, parent)

        # Injeção de dependência centralizada
        self.app = app_context
        self._is_initialized = False
        self._action_group = QtGui.QActionGroup(self)
        self._action_group.setExclusive(True)

        # Configuração base da toolbar
        self.setWindowTitle(title)
        self.setObjectName(title.lower().replace(" ", "_"))
        self.setMovable(is_movable)
        self.setFloatable(is_movable)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.setIconSize(QtCore.QSize(24, 24))

    # =========================================================================
    # Propriedades de Conveniência
    # =========================================================================

    @property
    def tool_manager(self) -> 'ToolManager':
        """Acesso facilitado ao tool_manager do contexto."""
        return self.app.tool_manager

    @property
    def scene_manager(self) -> 'SceneManager':
        """Acesso facilitado ao scene_manager do contexto."""
        return self.app.scene_manager

    @property
    def settings(self) -> Settings:
        """Acesso facilitado às configurações do contexto."""
        return self.app.settings

    # =========================================================================
    # Ciclo de Vida
    # =========================================================================

    def initialize(self) -> None:
        """
        Inicializa a toolbar chamando setup_ui().
        Pode ser chamado múltiplas vezes sem efeitos colaterais.
        """
        if not self._is_initialized:
            self.setup_ui()
            self._is_initialized = True

    def setup_ui(self) -> None:
        """
        Sobrescreva este método nas subclasses para adicionar ferramentas.
        Chamado automaticamente na inicialização.
        """
        pass

    def dispose(self) -> None:
        """
        Limpa recursos e remove todas as ações da toolbar.
        Deve ser chamado quando a toolbar não for mais necessária.
        """
        self.clear()
        self._is_initialized = False
        self._action_group = QtGui.QActionGroup(self)
        self._action_group.setExclusive(True)

    # =========================================================================
    # Registro de Ferramentas
    # =========================================================================

    def register_tool(self, tool: 'BaseTool') -> QtGui.QAction:
        """
        Registra uma ferramenta no ToolManager e cria um botão na toolbar.

        Args:
            tool: Instância da ferramenta a ser registrada

        Returns:
            Ação criada para a ferramenta
        """
        action = QtGui.QAction(tool.get_qicon(), tool.display_name, self)
        action.setCheckable(True)
        action.setToolTip(tool.tool_tip)
        action.setData(tool.name)  # Armazena o nome da ferramenta
        action.triggered.connect(
            lambda checked, t=tool: self._handle_tool_toggle(t, checked)
        )

        self._action_group.addAction(action)
        self.addAction(action)
        return action

    def _handle_tool_toggle(self, tool: 'BaseTool', checked: bool) -> None:
        """
        Gerencia ativação/desativação da ferramenta via ToolManager.
        Emite sinal tool_toggled para notificar outros componentes.
        """
        if checked:
            self.tool_manager.activate_tool(tool)
        else:
            # Só desativa se esta for a ferramenta ativa
            if self.tool_manager.active_tool == tool:
                self.tool_manager.deactivate_all()

        # Emite sinal para notificar mudança
        self.tool_toggled.emit(tool, checked)

    def get_active_tool(self) -> Optional['BaseTool']:
        """Retorna a ferramenta atualmente ativa."""
        return self.tool_manager.active_tool

    def deactivate_all_tools(self) -> None:
        """Desativa todas as ferramentas."""
        self.tool_manager.deactivate_all()

    # =========================================================================
    # Métodos de UI
    # =========================================================================

    def add_spacer(self) -> None:
        """Adiciona um espaçador para organizar grupos na toolbar."""
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.addWidget(spacer)

    def set_display_mode(self, mode: str) -> None:
        """
        Altera dinamicamente a exibição: 'icon', 'text' ou 'icon_text'.

        Args:
            mode: Modo de exibição ('icon', 'text', 'icon_text')
        """
        modes = {
            'icon': QtCore.Qt.ToolButtonIconOnly,
            'text': QtCore.Qt.ToolButtonTextOnly,
            'icon_text': QtCore.Qt.ToolButtonTextBesideIcon
        }
        self.setToolButtonStyle(modes.get(mode, QtCore.Qt.ToolButtonIconOnly))

    def add_tool_button(self,
                        tool_data: ToolData,
                        icon: Optional[QtGui.QIcon] = None) -> QtWidgets.QToolButton:
        """
        Cria e adiciona um botão à toolbar baseado em ToolData.

        Args:
            tool_data: Dados da ferramenta
            icon: Ícone opcional (se não fornecido, usa o do tool_data)

        Returns:
            Botão criado
        """
        btn = QtWidgets.QToolButton()
        btn.setText(tool_data.display_name)
        btn.setToolTip(tool_data.tool_tip)
        btn.setCheckable(tool_data.is_checkable)

        if icon:
            btn.setIcon(icon)
        elif tool_data.icon_path:
            # Tenta carregar ícone do caminho se fornecido
            from pathlib import Path
            icon_path = Path(tool_data.icon_path)
            if icon_path.exists():
                btn.setIcon(QtGui.QIcon(str(icon_path)))

        btn.clicked.connect(tool_data.callback)
        self.addWidget(btn)
        return btn

    def add_action_button(self,
                          text: str,
                          callback: Callable,
                          icon: Optional[QtGui.QIcon] = None,
                          tooltip: str = "",
                          shortcut: Optional[str] = None) -> QtGui.QAction:
        """
        Adiciona uma ação à toolbar.

        Args:
            text: Texto da ação
            callback: Função a ser chamada
            icon: Ícone opcional
            tooltip: Dica de ferramenta
            shortcut: Atalho de teclado (ex: "Ctrl+S")

        Returns:
            Ação criada
        """
        action = QtGui.QAction(text, self)
        if icon:
            action.setIcon(icon)
        if tooltip:
            action.setToolTip(tooltip)
        if shortcut:
            action.setShortcut(QtGui.QKeySequence(shortcut))
        action.triggered.connect(callback)
        self.addAction(action)
        return action

    def add_separator(self) -> None:
        """Adiciona um separador visual na toolbar."""
        self.addSeparator()

    def clear(self) -> None:
        """Limpa todas as ações da toolbar."""
        for action in self._action_group.actions():
            self._action_group.removeAction(action)
        super().clear()

    # =========================================================================
    # Helpers para ícones
    # =========================================================================

    def get_icon(self, icon_name: str, fallback: Optional[QtGui.QIcon] = None) -> QtGui.QIcon:
        """
        Carrega um ícone do sistema de arquivos.

        Args:
            icon_name: Nome do arquivo de ícone
            fallback: Ícone de fallback se não encontrar

        Returns:
            Ícone carregado ou fallback
        """
        from pathlib import Path
        from core.localization.translator import get_base_dir

        path = get_base_dir() / "appearance" / "icons" / icon_name
        if path.exists():
            return QtGui.QIcon(str(path))
        return fallback or QtWidgets.QApplication.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_FileIcon
        )


# =============================================================================
# Exemplo de Uso
# =============================================================================

if __name__ == "__main__":
    import sys


    # Mock das dependências para teste
    class MockToolManager:
        def __init__(self):
            self.active_tool = None

        def activate_tool(self, tool):
            self.active_tool = tool
            print(f"Tool ativada: {tool.name if hasattr(tool, 'name') else tool}")

        def deactivate_all(self):
            self.active_tool = None
            print("Todas as ferramentas desativadas")


    class MockSceneManager:
        pass


    class MockSettings:
        def get(self, key, default=None):
            return default

        def set(self, key, value):
            pass


    # Criar contexto
    app_context = AppContext(
        tool_manager=MockToolManager(),
        scene_manager=MockSceneManager(),
        settings=MockSettings()
    )

    # Criar aplicação
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()

    # Criar toolbar
    toolbar = BaseToolbar("Exemplo", app_context, main_window)

    # Adicionar botão com ação
    toolbar.add_action_button(
        "Teste",
        lambda: print("Botão clicado!"),
        tooltip="Botão de teste",
        shortcut="Ctrl+T"
    )

    toolbar.add_separator()

    # Adicionar espaçador
    toolbar.add_spacer()

    # Adicionar ao main window
    main_window.addToolBar(toolbar)
    main_window.setWindowTitle("BaseToolbar Test")
    main_window.resize(400, 200)
    main_window.show()

    sys.exit(app.exec())