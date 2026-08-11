from __future__ import annotations
from pathlib import Path
from typing import Optional
from PySide6 import QtWidgets, QtCore

from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory
from core.application.commands.volume.load_dicom_command import LoadDicomCommand

from domain.volume.dicom.validators.dicom_validator import DicomValidator
from domain.volume.windows.dicom_import_window import DicomImportWindow

# Settings
from core.settings.localization.translator import tr


class LoadDicomTool(BaseTool):
    name: str = "load_dicom"
    display_name: str = tr("tools.import.display_name", "Carregar DICOM / Tomografia")
    category: ToolCategory = ToolCategory.TOMOGRAPHY
    tool_tip: str = tr("tools.import.tooltip", "Importar tomografia computadorizada (DICOM)")
    icon: Optional[str] = "folder.svg"

    def __init__(self):
        super().__init__()
        self.validator = DicomValidator()

    def create_widget(self) -> QtWidgets.QWidget:
        """Cria e retorna o widget personalizado com texto antes do ícone para a toolbar."""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)

        # Abordagem com QLabel + ToolButton para garantir rigorosamente: Texto -> Ícone
        layout.addWidget(QtWidgets.QLabel(tr("import.volumes.dicom", "Load Dicom")))

        icon_btn = QtWidgets.QToolButton()
        icon_btn.setToolTip(self.tool_tip)
        icon_btn.setIcon(self.get_qicon())
        icon_btn.setCheckable(False)
        icon_btn.clicked.connect(self.execute_import)
        layout.addWidget(icon_btn)

        return container

    def on_activate(self) -> None:
        self.execute_import()
        QtCore.QTimer.singleShot(0, self.deactivate)

    def execute_import(self) -> None:
        parent_window = self.context.window if (self.context and hasattr(self.context, "window")) else None

        directory = QtWidgets.QFileDialog.getExistingDirectory(
            parent_window,
            tr("file_browser.select_directory_title", "Selecionar Pasta DICOM / Tomografia"),
            "",
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
        )

        if not directory:
            return

        caminho_pasta = Path(directory)

        resultado_validacao = self.validator.validate_directory(caminho_pasta)
        if not resultado_validacao.get("sucesso", False):
            erro_msg = resultado_validacao.get("erro", "Erro desconhecido ao validar diretório.")
            QtWidgets.QMessageBox.warning(parent_window, tr("common.warning", "Aviso de Importação"), erro_msg)
            return

        series_disponiveis = resultado_validacao.get("series", [])

        if not series_disponiveis:
            series_disponiveis = [{
                "number": 1,
                "description": caminho_pasta.name,
                "modality": "CT",
                "path": str(caminho_pasta)
            }]

        import_dialog = DicomImportWindow(series_list=series_disponiveis, parent=parent_window)
        if import_dialog.exec() != QtWidgets.QDialog.Accepted:
            return

        selected_series = import_dialog.get_selected_series()
        sampling_factors = import_dialog.get_sampling_factors()

        if not selected_series:
            return

        target_path = Path(selected_series.get("path", caminho_pasta))

        try:
            if self.scene and hasattr(self.scene, "command_manager"):
                command = LoadDicomCommand(target_path, self.scene, series_info=selected_series,
                                           sampling_factors=sampling_factors)
                success = self.scene.command_manager.execute(command)

                if not success:
                    QtWidgets.QMessageBox.critical(
                        parent_window,
                        tr("common.error", "Erro"),
                        tr("dialogs.error.message", "Falha ao executar o comando de carga do volume tridimensional.")
                    )
                    return
            else:
                QtWidgets.QMessageBox.warning(
                    parent_window,
                    tr("common.warning", "Aviso"),
                    "Gerenciador de comandos (CommandManager) ou Cena não encontrados no contexto."
                )
                return

            if self.events and hasattr(self.events, "emit"):
                self.events.emit("DICOM_LOADED", path=str(target_path), factors=sampling_factors)

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                parent_window,
                tr("common.critical_error", "Erro Crítico"),
                f"Ocorreu um erro inesperado ao processar os arquivos DICOM:\n{str(e)}"
            )

    def on_deactivate(self) -> None:
        pass


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    tool = LoadDicomTool()
    sys.exit(app.exec())