from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional
from PySide6 import QtWidgets, QtCore

from core.components.bases.base_tool.base_tool import BaseTool, ToolCategory

# Importa a Pipeline unificada
from domain.volume.dicom.pipelines.dicom_import_pipeline import DicomImportPipeline

# Settings
from core.settings.localization.translator import tr
from core.settings.settings_app_manager import settings

logger = logging.getLogger(f"OpenCMF.Tool.{__name__.split('.')[-1]}")

ORG_NAME = "OpenCMF"
APP_NAME = "TomographyModule"

class LoadDicomTool(BaseTool):
    name: str = "load_dicom"
    display_name: str = tr("tools.import.display_name", "Carregar DICOM / Tomografia")
    category: ToolCategory = ToolCategory.TOMOGRAPHY
    tool_tip: str = tr("tools.import.tooltip", "Importar tomografia computadorizada (DICOM)")
    icon: Optional[str] = "folder.svg"

    def __init__(self, event_bus: Optional[object] = None):
        super().__init__()
        self._injected_event_bus = event_bus

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
        try:
            self.execute_import()
        except Exception as e:
            logger.error(f"Erro ao ativar ferramenta: {e}", exc_info=True)
        finally:
            QtCore.QTimer.singleShot(0, self.deactivate)

    def execute_import(self) -> None:
        """Executa a importação de arquivos DICOM."""
        parent_window = self._get_parent_window()

        directory = self._select_dicom_directory(parent_window)
        if not directory:
            logger.info("Importação cancelada pelo usuário")
            return

        self._save_last_directory(directory)

        event_bus = self._get_event_bus(parent_window)
        scene = self._get_scene(parent_window)

        try:
            pipeline = DicomImportPipeline(
                parent=parent_window,
                scene=scene,
                event_bus=event_bus
            )
            pipeline.start(directory)
            logger.info(f"Importação DICOM iniciada: {directory}")
        except Exception as e:
            self._handle_import_error(e)
            raise

    def _get_parent_window(self):
        """Obtém a janela pai de forma segura."""
        return self.context.window if (self.context and hasattr(self.context, "window")) else None

    def _select_dicom_directory(self, parent_window):
        """Abre diálogo para seleção do diretório DICOM."""
        last_dir = settings.last_dicom_directory or str(Path.home())

        return QtWidgets.QFileDialog.getExistingDirectory(
            parent_window,
            tr("file_browser.select_directory_title", "Selecionar Pasta DICOM / Tomografia"),
            last_dir,
            QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
        )

    def _save_last_directory(self, directory: str) -> None:
        """Salva o diretório selecionado nas configurações."""
        settings.last_dicom_directory = directory

    def _get_event_bus(self, parent_window):
        """Obtém o event_bus de forma robusta e centralizada."""
        sources = [
            self._injected_event_bus,
            getattr(self, "events", None),
            getattr(self, "event_bus", None),
            getattr(self.context, "event_bus", None) if self.context else None,
            getattr(parent_window, "event_bus", None) if parent_window else None,
            getattr(self, "eventBus", None),
            getattr(QtWidgets.QApplication.instance(), "event_bus", None)
        ]

        for source in sources:
            if source:
                return source

        if parent_window:
            event_bus = self._find_event_bus_in_parents(parent_window)
            if event_bus:
                return event_bus

        if self.context and hasattr(self.context, "app_context"):
            app_context_bus = getattr(self.context.app_context, "event_bus", None)
            if app_context_bus:
                return app_context_bus

        logger.warning("Event bus não encontrado nas fontes disponíveis.")
        return None

    def _find_event_bus_in_parents(self, widget):
        """Busca event_bus na hierarquia de pais."""
        current = widget.parent()
        while current:
            for attr in ["event_bus", "events"]:
                if hasattr(current, attr) and getattr(current, attr):
                    return getattr(current, attr)
            current = current.parent()
        return None

    def _get_scene(self, parent_window):
        """Obtém a scene de forma centralizada com checagens seguras."""
        if getattr(self, "scene", None):
            return self.scene

        if self.context and hasattr(self.context, "scene") and self.context.scene:
            return self.context.scene

        if parent_window and hasattr(parent_window, "scene") and parent_window.scene:
            return parent_window.scene

        logger.warning("Scene não encontrada nas fontes disponíveis.")
        return None

    def _handle_import_error(self, error):
        """Trata erros durante a importação."""
        error_msg = str(error)
        logger.error(f"Falha na importação DICOM: {error_msg}", exc_info=True)
        QtWidgets.QMessageBox.critical(
            None,
            tr("error.import.title", "Erro na Importação"),
            tr("error.import.message", "Não foi possível importar os arquivos DICOM:\n{error}").format(error=error_msg)
        )

    def on_deactivate(self) -> None:
        pass


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    tool = LoadDicomTool()
    sys.exit(app.exec())