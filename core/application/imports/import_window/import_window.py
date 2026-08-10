from __future__ import annotations

from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QSplitter, QWidget, QMessageBox

# Panels
from core.application.imports.import_window.panels.category_panel import (
    CategoryPanel,
)
from core.application.imports.import_window.panels.source_panel import SourcePanel
from core.application.imports.import_window.panels.workspace.workspace_container import (
    WorkspaceContainer,
)

# Gerenciadores do Sistema
from core.application.patient.patient_manager import PatientManager
from core.application.imports.import_manager import ImporterRegistry, ImportManager
from core.application.scene.scene_manager import SceneManager


class ImportWindow(QMainWindow):
    """Janela principal de importação integrando os três painéis lado a lado."""

    def __init__(self, scene_manager: Optional[SceneManager] = None,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Gerenciador de Importações")
        self.resize(1200, 600)

        # Gerenciadores de Cena e Importação (Removida a atribuição duplicada)
        self.scene_manager = scene_manager
        self.import_manager = ImportManager(ImporterRegistry())

        # Widget Central e Layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)

        # Splitter principal horizontal para os 3 painéis
        splitter = QSplitter(Qt.Horizontal, self)

        # Instanciando os três painéis
        self.category_panel = CategoryPanel()  # Painel 1 (Categorias)
        self.source_panel = SourcePanel()  # Painel 2 (Origem / Local)
        self.workspace_container = WorkspaceContainer()  # Painel 3 (Workspace / Conteúdo)

        # O Painel 2 começa desativado/vazio até que o Painel 1 tenha uma seleção válida
        self.source_panel.setEnabled(False)

        # Adicionando os três diretamente ao splitter na horizontal
        splitter.addWidget(self.category_panel)
        splitter.addWidget(self.source_panel)
        splitter.addWidget(self.workspace_container)

        # Definindo tamanhos iniciais em pixels para forçar a renderização visível
        splitter.setSizes([250, 250, 700])

        # Definindo proporções de redimensionamento dinâmico
        splitter.setStretchFactor(0, 1)  # Painel 1
        splitter.setStretchFactor(1, 1)  # Painel 2
        splitter.setStretchFactor(2, 3)  # Painel 3

        main_layout.addWidget(splitter)

        # Conexão de Sinais
        self.category_panel.category_selected.connect(
            self._handle_category_selection
        )
        self.source_panel.source_selected.connect(self._handle_selection_change)

        # Conexão do sinal de clique do botão "Importar" vindos do WorkspaceContainer
        self.workspace_container.import_requested.connect(self._handle_import_action)

    def _handle_category_selection(self, category_id=None) -> None:
        """Gerencia a seleção do Painel 1: verifica se é subcategoria e gerencia o Painel 2."""
        current_cat = self.category_panel.tree.currentItem()
        cat_id = current_cat.data(0, 32) if current_cat else category_id

        # Condicional: O Painel 2 só é habilitado se for uma subcategoria (item filho)
        is_subCategory = current_cat and current_cat.parent() is not None

        if is_subCategory and cat_id:
            self.source_panel.setEnabled(True)
            if hasattr(self.source_panel, "load_sources_for_category"):
                self.source_panel.load_sources_for_category(cat_id)
        else:
            self.source_panel.setEnabled(False)
            if hasattr(self.source_panel, "tree") and hasattr(self.source_panel.tree, "clearSelection"):
                self.source_panel.tree.clearSelection()

        self._handle_selection_change()

    def _handle_selection_change(self, source_id=None) -> None:
        """Atualiza o WorkspaceContainer com base nas condicionais de categoria e origem."""
        current_cat = self.category_panel.tree.currentItem()

        # Compatibilidade caso o SourcePanel utilize árvore ou lista interna
        source_tree = getattr(self.source_panel, "tree", None)
        current_src = source_tree.currentItem() if source_tree and hasattr(source_tree, "currentItem") else None

        cat_id = current_cat.data(0, 32) if current_cat else None
        src_id = current_src.data(0, 32) if current_src and hasattr(current_src, "data") else source_id

        # O Painel 3 carrega o contexto dinâmico (onde o FileBrowserView atualizado é injetado)
        if cat_id and src_id and current_cat and current_cat.parent() is not None:
            self.workspace_container.update_context(cat_id, src_id)

    def _handle_import_action(self, selected_file_path: str | Path) -> None:
        """Executa a importação utilizando o PatientManager, o ImportManager e o SceneManager."""
        patient_mgr = PatientManager.get_instance()
        if not patient_mgr.current_path:
            QMessageBox.warning(
                self,
                "Aviso",
                "Nenhum paciente ativo encontrado. Selecione ou crie um paciente antes de importar."
            )
            return

        try:
            # Assegura que o caminho seja processado corretamente seja string ou Path
            file_path = Path(selected_file_path)

            # 1. Processa os dados brutos gerando o SceneObject através do ImportManager
            scene_object = self.import_manager.import_source(file_path)

            # 2. Adiciona o objeto formalmente à cena (disparando a renderização visual via SceneBridge)
            if scene_object and self.scene_manager:
                self.scene_manager.add_object(scene_object)

            # 3. Registra no dicionário de dados do paciente ativo
            patient_data = patient_mgr.data
            if "imports" not in patient_data:
                patient_data["imports"] = {}

            category_id = getattr(self.workspace_container, "current_category", None) or "general"
            if category_id not in patient_data["imports"]:
                patient_data["imports"][category_id] = []

            file_str = str(file_path)
            if file_str not in patient_data["imports"][category_id]:
                patient_data["imports"][category_id].append(file_str)

            # 4. Persiste as alterações no disco
            patient_mgr.save_current_data()

            QMessageBox.information(
                self,
                "Sucesso",
                "Arquivo importado e adicionado à cena com sucesso!"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro de Importação",
                f"Não foi possível importar o arquivo:\n{str(e)}"
            )


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ImportWindow()
    window.show()
    sys.exit(app.exec())