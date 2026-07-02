import os
import json
import sys
import random
from pathlib import Path
from typing import Optional, Dict

import vtkmodules.all as vtk
from PySide6 import QtWidgets, QtCore
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from modules.base_module.base import ModuloBase
from core.volume.segmentation_engine import SegmentacaoEngine

# Componentes de UI importados conforme estrutura do projeto
from core.components.toolboxes.object_manager_toolbox import ObjetoManagerWidget
from core.components.toolboxes.segmentation_toolbox import SegmentacaoWidget


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Segmentação"
        self.id = "modulo.segmentacao"

        self.vtk_widget: Optional[QVTKRenderWindowInteractor] = None
        self.renderer = vtk.vtkRenderer()
        self.engine_seg = SegmentacaoEngine()

        self.volume_data = None
        self.atores: Dict[str, vtk.vtkActor] = {}

        self.widget_seg = SegmentacaoWidget()
        self.widget_objetos = ObjetoManagerWidget()
        self._conectar_sinais()

    def _conectar_sinais(self):
        self.widget_seg.pathChanged.connect(self._on_path_changed)
        self.widget_seg.thresholdChanged.connect(self._on_hu_changed)
        self.widget_seg.solicitarMascara.connect(self._executar_threshold)
        self.widget_seg.solicitarExportarSTL.connect(self._executar_exportacao_stl)

        self.widget_objetos.objetoToggled.connect(self._toggle_visibilidade)
        self.widget_objetos.opacityChanged.connect(self._set_opacidade)
        self.widget_objetos.colorChanged.connect(self._set_cor)
        self.widget_objetos.deleteRequested.connect(self._remover_objeto)

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self.renderer.SetBackground(0.05, 0.05, 0.1)

        info_json = Path(caminho_paciente) / "projeto" / "info.json"
        if info_json.exists():
            try:
                with open(info_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                dicom_path = data.get("caminhos", {}).get("dicom", "")
                self.widget_seg.set_path(dicom_path)
                self._carregar_volume(dicom_path)
            except Exception:
                pass

        self._sincronizar_pasta_stl()

    def _carregar_volume(self, caminho_dicom: str):
        path_vti = Path(self.pasta_paciente) / "projeto" / "volume.vti"

        if path_vti.exists():
            reader = vtk.vtkXMLImageDataReader()
            reader.SetFileName(str(path_vti))
            reader.Update()
            self.volume_data = reader.GetOutput()
        elif caminho_dicom and os.path.exists(caminho_dicom):
            from core.volume.dicom_engine import DicomEngine
            self.volume_data = DicomEngine().carregar_volume(caminho_dicom)

    def _executar_threshold(self):
        if not self.volume_data:
            return QtWidgets.QMessageBox.warning(None, "Erro", "Volume não carregado.")

        self.engine_seg.gerar_mascara(self.volume_data, self.widget_seg.get_value())
        QtWidgets.QMessageBox.information(None, "Sucesso", "Máscara de segmentação gerada.")

    def _executar_exportacao_stl(self):
        if not self.engine_seg.mask_data:
            return QtWidgets.QMessageBox.warning(None, "Aviso", "Gere a máscara primeiro.")

        dir_stl = Path(self.pasta_paciente) / "STL"
        dir_stl.mkdir(parents=True, exist_ok=True)
        caminho_saida = dir_stl / "segmentacao_hu.stl"

        if self.engine_seg.exportar_stl(self.engine_seg.mask_data, caminho_saida,
                                        self.widget_seg.get_qualidade_index()):
            self._sincronizar_pasta_stl()

    def _sincronizar_pasta_stl(self):
        pasta_stl = Path(self.pasta_paciente) / "STL"
        pasta_stl.mkdir(parents=True, exist_ok=True)

        for file_path in pasta_stl.glob("*.stl"):
            nome = file_path.name
            if nome not in self.atores:
                self._adicionar_malha_ao_render(file_path)

    def _adicionar_malha_ao_render(self, file_path: Path):
        nome = file_path.name
        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(file_path))
        reader.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        cor_random = [random.random() for _ in range(3)]
        actor.GetProperty().SetColor(cor_random)

        self.renderer.AddActor(actor)
        self.atores[nome] = actor
        self.widget_objetos.adicionar_objeto_lista(nome, "Segmentação", cor_random)
        self._renderizar()

    def _toggle_visibilidade(self, nome, estado):
        if nome in self.atores:
            self.atores[nome].SetVisibility(estado)
            self._renderizar()

    def _set_opacidade(self, nome, valor):
        if nome in self.atores:
            self.atores[nome].GetProperty().SetOpacity(valor)
            self._renderizar()

    def _set_cor(self, nome, qcolor):
        if nome in self.atores:
            self.atores[nome].GetProperty().SetColor(qcolor.redF(), qcolor.greenF(), qcolor.blueF())
            self._renderizar()

    def _remover_objeto(self, nome):
        actor = self.atores.pop(nome, None)
        if actor:
            self.renderer.RemoveActor(actor)
            path = Path(self.pasta_paciente) / "STL" / nome
            if path.exists():
                os.remove(path)
            self._renderizar()

    def _on_path_changed(self, path):
        if os.path.exists(path):
            self._carregar_volume(path)

    def _on_hu_changed(self, val):
        pass  # Implementar preview em tempo real se a engine suportar

    def _renderizar(self):
        if self.vtk_widget:
            self.vtk_widget.GetRenderWindow().Render()

    def get_workspace(self) -> QtWidgets.QWidget:
        if not self.vtk_widget:
            self.vtk_widget = QVTKRenderWindowInteractor()
            self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
            self.vtk_widget.Initialize()
        return self.vtk_widget

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        return {
            "Ferramentas": self.widget_seg,
            "Objetos": self.widget_objetos
        }


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    modulo = Modulo()
    path_teste = Path(os.path.expanduser("~")) / "OpenCMF_Debug"
    path_teste.mkdir(parents=True, exist_ok=True)
    (path_teste / "STL").mkdir(exist_ok=True)
    (path_teste / "projeto").mkdir(exist_ok=True)

    modulo.inicializar(str(path_teste))

    win = QtWidgets.QMainWindow()
    win.setWindowTitle("OpenCMF - Segmentação")
    win.setCentralWidget(modulo.get_workspace())

    dock = QtWidgets.QDockWidget("Controles")
    tabs = QtWidgets.QTabWidget()
    for n, w in modulo.get_toolboxes().items():
        tabs.addTab(w, n)
    dock.setWidget(tabs)

    win.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
    win.resize(1200, 800)
    win.show()
    sys.exit(app.exec())