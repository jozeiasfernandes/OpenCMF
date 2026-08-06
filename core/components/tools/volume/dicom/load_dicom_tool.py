from __future__ import annotations
from pathlib import Path
from typing import Optional
from PySide6 import QtWidgets, QtCore

from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory
from domain.volume.dicom.validators.dicom_validator import DicomValidator
from application.commands.volume.load_dicom_command import LoadDicomCommand


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
        resultado_validacao = self.validator.validar_diretorio(caminho_pasta)
        if not resultado_validacao.get("sucesso", False):
            erro_msg = resultado_validacao.get("erro", "Erro desconhecido ao validar diretório.")
            QtWidgets.QMessageBox.warning(parent_window, "Aviso de Importação", erro_msg)
            return

        # 2. Execução segura encapsulada no Command Pattern via SceneManager
        try:
            if self.scene and hasattr(self.scene, "command_manager"):
                command = LoadDicomCommand(caminho_pasta, self.scene)
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
                self.events.emit("DICOM_LOADED", path=str(caminho_pasta))

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