import json
import vtk
import os
import sys
from pathlib import Path

root_path = str(Path(__file__).parent.parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

from typing import Dict, Optional
from PySide6 import QtWidgets, QtCore

from modules.base_module.base_module import ModuloBase
from core.volume.dicom_engine import DicomEngine
from core.volume.viewer import VolumeViewerWidget
from core.volume.validator import DicomValidator

from modules.mod_tomography.ui import TomografiaUI
from core.components.toolbars.tomography_toolbar import TomographyToolbar

class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Tomografia"
        self.id = "modulo.tomografia"
        self.engine = DicomEngine()
        self.ui = TomografiaUI()
        self.toolbar_handler: Optional[TomographyToolbar] = None
        self.viewer: Optional[VolumeViewerWidget] = None
        self.caminho_dicom: Optional[str] = None
        self._is_initialized = False

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self._carregar_configs_projeto()

    def _carregar_configs_projeto(self):
        path_info = Path(self.pasta_paciente) / "projeto" / "info.json"
        if not path_info.exists():
            return
        try:
            with open(path_info, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.caminho_dicom = dados.get("caminhos", {}).get("dicom")
                if self.caminho_dicom:
                    self.ui.edit_dicom.setText(self.caminho_dicom)
        except Exception as e:
            print(f"Erro ao carregar info.json: {e}")

    def _atualizar_persistencia_diretorio(self, novo_caminho: str):
        path_info = Path(self.pasta_paciente) / "projeto" / "info.json"
        try:
            dados = {}
            if path_info.exists():
                with open(path_info, "r", encoding="utf-8") as f:
                    dados = json.load(f)

            dados.setdefault("caminhos", {})["dicom"] = novo_caminho
            self.caminho_dicom = novo_caminho

            path_info.parent.mkdir(parents=True, exist_ok=True)
            with open(path_info, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao persistir caminho no JSON: {e}")

    def _buscar_pasta(self):
        settings = QtCore.QSettings("OpenCMF", "Config")
        ultimo = settings.value("ultimo_diretorio_dicom", "")
        pasta = QtWidgets.QFileDialog.getExistingDirectory(None, "Selecionar Pasta DICOM", ultimo)
        if pasta:
            self.ui.edit_dicom.setText(pasta)
            settings.setValue("ultimo_diretorio_dicom", pasta)

    def _validar_dicom(self):
        caminho_input = self.ui.edit_dicom.text()
        if not caminho_input: return

        progresso = self._criar_progresso("Validador DICOM", "Analisando estrutura...")
        validador = DicomValidator(self.pasta_paciente)
        resultado = validador.analisar_caminho(
            caminho_input,
            callback=lambda m, v: self._update_progresso(progresso, m, v)
        )
        progresso.close()

        if not resultado["sucesso"]:
            QtWidgets.QMessageBox.critical(None, "Erro", resultado["erro"])
            return

        series = resultado["series"]
        ids = list(series.keys())
        id_escolhido = ids[0]

        if len(ids) > 1:
            opcoes = [f"{series[s][0]['desc']} ({len(series[s])} fatias)" for s in ids]
            item, ok = QtWidgets.QInputDialog.getItem(None, "Múltiplas Séries", "Escolha a série:", opcoes, 0, False)
            if not ok: return
            id_escolhido = ids[opcoes.index(item)]

        caminho_final = str(Path(series[id_escolhido][0]["path"]).parent)
        self._atualizar_persistencia_diretorio(caminho_final)

        self.ui.update_status_validado()
        if self.toolbar_handler:
            self.toolbar_handler.set_validation_state(True)

    def _carregar_dicom(self):
        if not self.caminho_dicom: return

        progresso = self._criar_progresso("Carregador", "Lendo fatias DICOM...")
        try:
            progresso.setValue(20)
            sucesso, msg = self.engine.carregar_pasta(self.caminho_dicom)

            if sucesso:
                progresso.setValue(70)
                if self.viewer:
                    self.viewer.set_volume(self.engine.vtk_volume)
                    self.ui.update_status_carregado()
                progresso.setValue(100)
            else:
                QtWidgets.QMessageBox.critical(None, "Erro", msg)
        finally:
            progresso.close()

    def _gerar_vti(self):
        if not self.engine.vtk_volume: return

        progresso = self._criar_progresso("Exportador", "Gerando arquivo VTI...")
        try:
            progresso.setValue(30)
            path_vti = Path(self.pasta_paciente) / "projeto" / "volume.vti"
            path_vti.parent.mkdir(parents=True, exist_ok=True)

            writer = vtk.vtkXMLImageDataWriter()
            writer.SetFileName(str(path_vti))
            writer.SetInputData(self.engine.vtk_volume)
            writer.SetCompressorTypeToZLib()
            writer.Write()

            self._is_initialized = True
            self.ui.update_status_vti_gerado()
            progresso.setValue(100)
            QtWidgets.QMessageBox.information(None, "Sucesso", "Volume persistido com sucesso!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Erro", f"Falha ao salvar VTI: {e}")
        finally:
            progresso.close()

    def _criar_progresso(self, titulo, msg):
        pd = QtWidgets.QProgressDialog(msg, "Cancelar", 0, 100, None)
        pd.setWindowTitle(titulo)
        pd.setWindowModality(QtCore.Qt.WindowModal)
        pd.show()
        return pd

    def _update_progresso(self, pd, msg, valor):
        pd.setLabelText(msg)
        pd.setValue(valor)
        QtWidgets.QApplication.processEvents()

    def _finalizar_etapa(self):
        if not self._is_initialized:
            QtWidgets.QMessageBox.warning(None, "Aviso", "Gere o volume VTI antes de prosseguir.")
            return
        self.concluido.emit()

    def _wl_manual(self, window: float, level: float):
        if self.viewer:
            self.viewer.update_window_level(window, level)

    def get_workspace(self) -> QtWidgets.QWidget:
        if self.viewer:
            self.viewer.deleteLater()

        self.viewer = VolumeViewerWidget()
        self.viewer.windowLevelChanged.connect(self.ui.update_wl_ui)

        if self.engine.vtk_volume:
            self.viewer.set_volume(self.engine.vtk_volume)
            self.ui.update_status_carregado()

        return self.viewer

    def get_workspace_toolbar(self) -> QtWidgets.QToolBar:
        toolbar = QtWidgets.QToolBar("Tomografia")
        self.toolbar_handler = TomographyToolbar(toolbar)

        self.toolbar_handler.importDicomRequested.connect(self._buscar_pasta)
        self.toolbar_handler.validateRequested.connect(self._validar_dicom)
        self.toolbar_handler.loadVolumeRequested.connect(self._carregar_dicom)
        self.toolbar_handler.exportVtiRequested.connect(self._gerar_vti)

        self.toolbar_handler.resetViewRequested.connect(
            lambda: self.viewer.refresh_display() if self.viewer else None
        )

        self.toolbar_handler.layoutChanged.connect(
            lambda layout: self.viewer.configurar_layout(layout) if self.viewer else None
        )

        self.toolbar_handler.colorMapChanged.connect(
            lambda lut: self.viewer.apply_global_lut(lut) if self.viewer else None
        )

        if self.caminho_dicom:
            self.toolbar_handler.set_validation_state(False)

        return toolbar

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return self.ui.setup_toolboxes(
            on_buscar=self._buscar_pasta,
            on_validar=self._validar_dicom,
            on_carregar=self._carregar_dicom,
            on_gerar_vti=self._gerar_vti,
            on_wl_manual=self._wl_manual,
            on_finalizar=self._finalizar_etapa
        )

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    temp_path = os.path.abspath("./teste_paciente")
    os.makedirs(os.path.join(temp_path, "projeto"), exist_ok=True)

    modulo = Modulo()
    modulo.inicializar(temp_path)

    window = QtWidgets.QMainWindow()
    window.setWindowTitle(f"Standalone - {modulo.nome}")
    window.resize(1024, 768)

    toolbar = modulo.get_workspace_toolbar()
    window.addToolBar(toolbar)

    workspace = modulo.get_workspace()
    window.setCentralWidget(workspace)

    toolboxes = modulo.get_toolboxes()
    dock = QtWidgets.QDockWidget("Ferramentas", window)
    container_abas = QtWidgets.QTabWidget()
    for nome, widget in toolboxes.items():
        container_abas.addTab(widget, nome)
    dock.setWidget(container_abas)
    window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

    window.show()
    sys.exit(app.exec())