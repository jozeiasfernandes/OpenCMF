#               pytest test/main/test_main.py

import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_path))

from unittest.mock import MagicMock, patch
import pytest
from PySide6 import QtWidgets, QtCore

from main import MainWindow, ApplicationContext


class MockHomePage(QtWidgets.QWidget):
    """Simula a Home_page incluindo o sinal personalizado esperado pelo MainWindow."""
    projeto_selecionado = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.update_list = MagicMock()


class MockWorkspaceManager(QtWidgets.QWidget):
    """Simula o WorkspaceManager mantendo compatibilidade com QWidget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_bar_manager = MagicMock()


@pytest.fixture
def qapp():
    """Garante que existe uma instância única de QApplication rodando para os testes."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    yield app


@pytest.fixture
def mock_dependencies():
    """Configura os mocks utilizando classes compatíveis com QWidget e Qt Signals."""
    home_mock = MockHomePage()
    workspace_mock = MockWorkspaceManager()

    with patch("main.Home_page", return_value=home_mock), \
            patch("main.PaginaEditorFluxo", side_effect=lambda: QtWidgets.QWidget()), \
            patch("main.WorkspaceManager", return_value=workspace_mock), \
            patch("main.PaginaConfig", side_effect=lambda workspace_manager=None: QtWidgets.QWidget()), \
            patch("main.ProjectServiceHomePage"), \
            patch("main.SceneManager"), \
            patch("main.ToolManager"):
        yield {
            "home": home_mock,
            "flow": QtWidgets.QWidget(),
            "workspace": workspace_mock,
            "config": QtWidgets.QWidget(),
        }


def test_main_window_initialization(qapp, qtbot, mock_dependencies):
    """Testa se a MainWindow inicializa corretamente e configura o stack de widgets."""
    with patch("pathlib.Path.exists", return_value=True), \
            patch("pathlib.Path.read_text", return_value=""), \
            patch("core.settings.settings_app_manager.SettingsManager.tema", "dark"):
        window = MainWindow()
        qtbot.addWidget(window)

        assert window is not None
        assert isinstance(window.centralWidget(), QtWidgets.QStackedWidget)
        assert isinstance(window.context, ApplicationContext)


def test_navigation_back_to_home(qapp, qtbot, mock_dependencies):
    """Testa se o método back_to_home altera a página atual no QStackedWidget."""
    with patch("pathlib.Path.exists", return_value=True), \
            patch("pathlib.Path.read_text", return_value=""), \
            patch("core.settings.settings_app_manager.SettingsManager.tema", "dark"):
        window = MainWindow()
        qtbot.addWidget(window)

        window.back_to_home()

        assert window.stack.currentWidget() == mock_dependencies["home"]
        mock_dependencies["home"].update_list.assert_called_once()


def test_start_workflow_error_handling(qapp, qtbot, mock_dependencies):
    """Testa o comportamento de start_workflow ao receber um arquivo JSON inválido ou inexistente."""
    with patch("pathlib.Path.exists", return_value=True), \
            patch("pathlib.Path.read_text", return_value=""), \
            patch("core.settings.settings_app_manager.SettingsManager.tema", "dark"):
        window = MainWindow()
        qtbot.addWidget(window)

        window.start_workflow("caminho/inexistente/flow.json")

        mock_dependencies["workspace"].status_bar_manager.showMessage.assert_called()