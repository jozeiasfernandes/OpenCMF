from PySide6 import QtWidgets, QtCore
from .registry import WorkspaceRegistry
from .state import WorkspaceState
from .layout import ModuleLayoutBuilder
from .components.status_bar import StatusBarManager
from .components.tab_controller import TabController
from core.workspace.module_factory import ModuleFactory


class Manager(QtWidgets.QMainWindow):
    home_solicitada = QtCore.Signal()
    current_module_changed = QtCore.Signal()
    def __init__(self, parent=None):
        super().__init__(parent)

        self.state = WorkspaceState()
        self.registry = WorkspaceRegistry()
        self.layout_builder = ModuleLayoutBuilder()
        self.status_bar = StatusBarManager()
        self.container = QtWidgets.QStackedWidget()

        # 1. Crie o controller PRIMEIRO (passando o container que já existe)
        self.tab_controller = TabController(self.container)
        self.tab_controller.tab_closed.connect(self._on_tab_closed)

        # 2. Agora crie a barra visível usando o layout que o controller criou
        self.tab_bar_widget = QtWidgets.QWidget()
        self.tab_bar_widget.setLayout(self.tab_controller.tab_bar_layout)

        # 3. Layout principal
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.tab_bar_widget)
        main_layout.addWidget(self.container)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setStatusBar(self.status_bar)
        self.state.config_changed.connect(self._handle_config_change)
        self.container.currentChanged.connect(self.current_module_changed)

    def open_module(self, module_id: str, title: str):
        self.status_bar.start_loading(f"Carregando {module_id}...")

        try:
            module = self.registry.get_or_create_module(module_id)

            widget = self.layout_builder.build(module)

            self.tab_controller.add_tab(title, widget)

            new_index = self.tab_controller.tabs.index(self.tab_controller.tabs[-1])
            self.tab_controller.set_active(new_index)

        except Exception as e:
            # Importante adicionar tratamento de erro para não travar a UI
            print(f"Erro ao abrir módulo {module_id}: {e}")
            self.status_bar.update_message("Erro ao carregar módulo.")
        finally:
            self.status_bar.stop_loading()

    def _handle_config_change(self, new_config: dict):
        """Reage a mudanças nas configurações globais."""
        current_widget = self.container.currentWidget()
        if current_widget:
            self.layout_builder.refresh(current_widget, new_config)

    def close_current_module(self):
        current_index = self.container.currentIndex()
        if current_index == -1:
            return
        self._on_tab_closed(current_index)

    def _on_tab_closed(self, index: int):
        # Remove o widget do container
        widget = self.container.widget(index)
        if widget:
            self.container.removeWidget(widget)
            widget.deleteLater()

        # Remove a aba da lista de tabs do controller
        if hasattr(self.tab_controller, 'tabs'):
            if index < len(self.tab_controller.tabs):
                self.tab_controller.tabs.pop(index)

    def clear(self):
        while self.container.count() > 0:
            widget = self.container.widget(0)
            self.container.removeWidget(widget)
            widget.deleteLater()

        if hasattr(self.tab_controller, 'tabs'):
            self.tab_controller.tabs.clear()

    def get_modulo_ativo(self):
        return self.container.currentWidget()

    def set_patient_path(self, path: str):
        self.state.patient_path = path

if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from PySide6 import QtWidgets


    class MockModule:
        def get_main_widget(self):
            return QtWidgets.QLabel("Conteúdo Principal do Módulo")

        def get_toolbox_widget(self):
            return QtWidgets.QLabel("Painel de Ferramentas")

        def cleanup(self):
            print("Módulo limpo com sucesso!")

    app = QtWidgets.QApplication(sys.argv)

    ModuleFactory.register("mock_id", MockModule)

    manager = Manager()
    manager.resize(1024, 768)
    manager.show()

    manager.open_module("mock_id", "Teste de Módulo")

    sys.exit(app.exec())