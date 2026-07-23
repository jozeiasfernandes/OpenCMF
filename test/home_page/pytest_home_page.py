import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_path))

from unittest.mock import MagicMock, patch
import pytest
from PySide6 import QtWidgets

from core.home_page.home_page import Home_page


@pytest.fixture
def qapp():
    """Garante que existe uma instância única de QApplication rodando para os testes."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    yield app


@pytest.fixture
def mock_home_services():
    """Mocka os serviços utilizando o caminho exato de importação dentro de home_page.py."""
    with patch("core.home_page.home_page.ProjectServiceHomePage") as mock_project_service, \
            patch("core.home_page.home_page.FlowServiceHomePage") as mock_flow_service, \
            patch("core.icons.icons_manager.IconManager.get_instance") as mock_get_icon_instance:
        proj_instance = mock_project_service.return_value
        proj_instance.list_recent_projects.return_value = [
            {"_path": "caminho/projeto/mock.json", "paciente": {"nome": "Paciente Teste"}}
        ]

        flow_instance = mock_flow_service.return_value
        flow_instance.list_flows.return_value = [
            {"_file_path": "caminho/fluxo/mock.json", "name": "Fluxo Teste"}
        ]

        icon_instance = mock_get_icon_instance.return_value
        icon_instance.get_icon.return_value = QtWidgets.QWidget().style().standardIcon(QtWidgets.QStyle.SP_FileIcon)
        icon_instance.get_color.return_value = "#FFFFFF"

        yield {
            "project_service": proj_instance,
            "flow_service": flow_instance,
        }


def test_home_page_initialization(qapp, qtbot, mock_home_services):
    """Testa se a Home_page inicializa corretamente carregando os componentes de UI e dados."""
    with patch("pathlib.Path.exists", return_value=True), \
            patch("pathlib.Path.read_text", return_value=""), \
            patch("core.settings.settings_app_manager.SettingsManager.tema", "dark"):
        home = Home_page()
        qtbot.addWidget(home)

        assert home is not None
        assert isinstance(home, QtWidgets.QWidget)
        mock_home_services["project_service"].list_recent_projects.assert_called()
        mock_home_services["flow_service"].list_flows.assert_called()


def test_toggle_view_mode(qapp, qtbot, mock_home_services):
    """Testa se a alternância entre visualização em lista e grade funciona corretamente."""
    with patch("pathlib.Path.exists", return_value=True), \
            patch("pathlib.Path.read_text", return_value=""), \
            patch("core.settings.settings_app_manager.SettingsManager.tema", "dark"):
        home = Home_page()
        qtbot.addWidget(home)

        assert home.is_grid_view is False
        assert home.view_container.currentIndex() == 0

        home._toggle_view_mode()

        assert home.is_grid_view is True
        assert home.view_container.currentIndex() == 1


def test_toggle_search_bar(qapp, qtbot, mock_home_services):
    """Testa se a visibilidade da barra de busca de projetos é alternada corretamente."""
    with patch("pathlib.Path.exists", return_value=True), \
            patch("pathlib.Path.read_text", return_value=""), \
            patch("core.settings.settings_app_manager.SettingsManager.tema", "dark"):
        home = Home_page()
        home.show()
        qtbot.addWidget(home)

        # Assegura o estado inicial controlado para o teste de visibilidade
        home.search_input.setVisible(False)
        assert home.search_input.isVisible() is False

        home._toggle_search()
        assert home.search_input.isVisible() is True

        home._toggle_search()
        assert home.search_input.isVisible() is False