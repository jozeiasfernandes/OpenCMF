from __future__ import annotations
from pathlib import Path
from typing import Optional
from PySide6 import QtWidgets, QtCore

from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory

# Importa a Pipeline unificada
from domain.volume.dicom.pipelines.dicom_import_pipeline import DicomImportPipeline

# Settings
from core.settings.localization.translator import tr

ORG_NAME = "OpenCMF"
APP_NAME = "TomographyModule"

class LoadDicomTool(BaseTool):
    name: str = "load_dicom"
    display_name: str = tr("tools.import.display_name", "Carregar DICOM / Tomografia")
    category: ToolCategory = ToolCategory.TOMOGRAPHY
    tool_tip: str = tr("tools.import.tooltip", "Importar tomografia computadorizada (DICOM)")
    icon: Optional[str] = "folder.svg"

    def __init__(self):
        super().__init__()
        # O validador, engine e regras agora ficam encapsulados na Pipeline

    def create_widget(self) -> QtWidgets.QWidget:
        """Cria e retorna um widget personalizado com o texto antes do ícone em um único bloco clicável."""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        btn = QtWidgets.QToolButton()
        btn.setToolTip(self.tool_tip)
        btn.setText(tr("import.volumes.dicom", "Load Dicom"))
        btn.setIcon(self.get_qicon())
        btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        btn.setCheckable(False)
        btn.clicked.connect(self.execute_import)

        layout.addWidget(btn)
        return container

    def on_activate(self) -> None:
        self.execute_import()
        QtCore.QTimer.singleShot(0, self.deactivate)

    def execute_import(self) -> None:
        parent_window = self.context.window if (self.context and hasattr(self.context, "window")) else None

        # Recupera a última pasta salva no registro do sistema (retorna "" se não houver)
        settings = QtCore.QSettings(ORG_NAME, APP_NAME)
        last_dir = settings.value("last_dicom_directory", "")

        directory = QtWidgets.QFileDialog.getExistingDirectory(
            parent_window,
            tr("file_browser.select_directory_title", "Selecionar Pasta DICOM / Tomografia"),
            last_dir,  # Define o diretório inicial como a última pasta lembrada
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
        )

        if not directory:
            return

        # Salva o novo diretório selecionado na memória persistente para uso futuro
        settings.setValue("last_dicom_directory", directory)

        # Busca o event_bus e a scene de forma robusta nas várias camadas da aplicação
        event_bus = (
            getattr(self, "events", None) or
            getattr(self.context, "event_bus", None) or
            getattr(parent_window, "event_bus", None) or
            getattr(self, "eventBus", None)
        )

        # Varredura recursiva nos widgets pais do Qt caso ainda não tenha encontrado
        if not event_bus and parent_window:
            p = parent_window.parent()
            while p:
                if hasattr(p, "event_bus"):
                    event_bus = p.event_bus
                    break
                if hasattr(p, "events"):
                    event_bus = p.events
                    break
                p = p.parent()

        # Se ainda assim o event_bus estiver vazio, tenta obtê-lo da aplicação global se houver
        if not event_bus and hasattr(QtWidgets.QApplication.instance(), "event_bus"):
            event_bus = QtWidgets.QApplication.instance().event_bus

        scene = (
            getattr(self, "scene", None) or
            getattr(self.context, "scene", None) or
            getattr(parent_window, "scene", None)
        )

        pipeline = DicomImportPipeline(
            parent=parent_window,
            scene=scene,
            event_bus=event_bus
        )

        pipeline.start(directory)

    def on_deactivate(self) -> None:
        pass


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    tool = LoadDicomTool()
    sys.exit(app.exec())