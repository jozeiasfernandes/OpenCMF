from __future__ import annotations
from pathlib import Path
from typing import Optional
from PySide6 import QtWidgets, QtCore

from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory
from domain.volume.dicom.validators.dicom_validator import DicomValidator
from core.application.commands.volume.load_dicom_command import LoadDicomCommand
from domain.volume.windows.dicom_import_window import DicomImportWindow


class LoadDicomTool(BaseTool):
    name: str = "load_dicom"
    display_name: str = "Carregar DICOM / Tomografia"
    category: ToolCategory = ToolCategory.TOMOGRAPHY
    tool_tip: str = "Importar tomografia computadorizada (DICOM)"
    icon: Optional[str] = "open_folder.png"

    def __init__(self):
        super().__init__()
        self.validator = DicomValidator()

    def on_activate(self) -> None:
        """Executado automaticamente quando a ferramenta é acionada na toolbar."""
        self.execute_import()
        # Ferramenta de ação pontual: desativa logo após a execução
        QtCore.QTimer.singleShot(0, self.deactivate)

    def execute_import(self) -> None:
        parent_window = self.context.window if (self.context and hasattr(self.context, "window")) else None

        directory = QtWidgets.QFileDialog.getExistingDirectory(
            parent_window,
            "Selecionar Pasta DICOM / Tomografia",
            "",
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
        )

        if not directory:
            return

        caminho_pasta = Path(directory)

        # 1. Validação prévia da pasta usando o DicomValidator
        resultado_validacao = self.validator.validate_directory(caminho_pasta)
        if not resultado_validacao.get("sucesso", False):
            erro_msg = resultado_validacao.get("erro", "Erro desconhecido ao validar diretório.")
            QtWidgets.QMessageBox.warning(parent_window, "Aviso de Importação", erro_msg)
            return

        # Recupera as séries encontradas pelo validador
        series_disponiveis = resultado_validacao.get("series", [])

        # Fallback de segurança caso a estrutura retorne sucesso genérico sem lista detalhada
        if not series_disponiveis:
            series_disponiveis = [{
                "number": 1,
                "description": caminho_pasta.name,
                "modality": "CT",
                "path": str(caminho_pasta)
            }]

        # 2. Exibe a janela de importação/seleção de séries ao usuário
        import_dialog = DicomImportWindow(series_list=series_disponiveis, parent=parent_window)
        if import_dialog.exec() != QtWidgets.QDialog.Accepted:
            return

        selected_series = import_dialog.get_selected_series()
        sampling_factors = import_dialog.get_sampling_factors()  # (X, Y, Z)

        if not selected_series:
            return

        # Define o caminho alvo (diretório específico da série selecionada ou a raiz)
        target_path = Path(selected_series.get("path", caminho_pasta))

        # 3. Execução segura encapsulada no Command Pattern via SceneManager
        try:
            if self.scene and hasattr(self.scene, "command_manager"):
                # Repassa os fatores de amostragem e a série escolhida para o comando
                command = LoadDicomCommand(target_path, self.scene, series_info=selected_series,
                                           sampling_factors=sampling_factors)
                success = self.scene.command_manager.execute(command)

                if not success:
                    QtWidgets.QMessageBox.critical(
                        parent_window,
                        "Erro",
                        "Falha ao executar o comando de carga do volume tridimensional."
                    )
                    return
            else:
                QtWidgets.QMessageBox.warning(
                    parent_window,
                    "Aviso",
                    "Gerenciador de comandos (CommandManager) ou Cena não encontrados no contexto."
                )
                return

            if self.events and hasattr(self.events, "emit"):
                self.events.emit("DICOM_LOADED", path=str(target_path), factors=sampling_factors)

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                parent_window,
                "Erro Crítico",
                f"Ocorreu um erro inesperado ao processar os arquivos DICOM:\n{str(e)}"
            )

    def on_deactivate(self) -> None:
        pass


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    tool = LoadDicomTool()
    print(f"Ferramenta inicializada: {tool.display_name}")
    print(f"Categoria: {tool.category.name}")

    sys.exit(app.exec())