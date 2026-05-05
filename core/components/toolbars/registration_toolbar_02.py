import sys
from pathlib import Path
from typing import Dict, Optional

from PySide6 import QtWidgets, QtCore, QtGui
import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from core.components.toolbars.imports.import_panel import ImportObjectsPanel
from core.imports.object_manager import ObjectManager
from core.imports.models_import import ObjectProperties


class RegistrationToolbarHandler(QtCore.QObject):
    importRequested = QtCore.Signal(str, str)
    pointSizeChanged = QtCore.Signal(float)

    def __init__(self, toolbar: QtWidgets.QToolBar):
        super().__init__()
        self.toolbar = toolbar
        self._setup_ui()

    def _setup_ui(self):
        self.btn_import = QtWidgets.QPushButton("Import")
        self.toolbar.addWidget(self.btn_import)

        self.import_panel = ImportObjectsPanel(self.toolbar)
        self.import_panel.importRequested.connect(self.importRequested.emit)
        self.btn_import.clicked.connect(
            lambda: self.import_panel.show_under(self.btn_import)
        )

        self.toolbar.addSeparator()
        self.toolbar.addWidget(QtWidgets.QLabel(" Size: "))

        self.slider_size = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_size.setRange(5, 50)
        self.slider_size.setFixedWidth(60)
        self.slider_size.valueChanged.connect(
            lambda v: self.pointSizeChanged.emit(v / 10.0)
        )
        self.toolbar.addWidget(self.slider_size)


class Component(QtWidgets.QToolBar):
    def __init__(self, modulo=None):
        super().__init__()
        self.modulo = modulo
        self.setWindowTitle("Alinhar objetos")
        self.__module_path__ = Path(__file__).resolve()

        self.handler = RegistrationToolbarHandler(self)


class ObjetoManagerWidget(QtWidgets.QWidget):
    objetoToggled = QtCore.Signal(str, bool)
    opacityChanged = QtCore.Signal(str, float)
    colorChanged = QtCore.Signal(str, QtGui.QColor)
    deleteRequested = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cats: Dict[str, QtWidgets.QTreeWidgetItem] = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderLabels(["Objeto", "Opacidade", "Cor"])
        self.tree_widget.setIndentation(12)
        self.tree_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self._show_context_menu)

        header = self.tree_widget.header()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        self.tree_widget.setColumnWidth(1, 80)
        self.tree_widget.setColumnWidth(2, 35)

        self.tree_widget.itemChanged.connect(self._handle_item_changed)
        layout.addWidget(self.tree_widget)

    def _get_or_create_category(self, cat_name: str):
        if cat_name not in self.cats:
            item = QtWidgets.QTreeWidgetItem(self.tree_widget)
            item.setText(0, cat_name.upper())
            item.setExpanded(True)
            item.setFirstColumnSpanned(True)

            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)
            item.setBackground(0, QtGui.QColor(60, 60, 60))
            self.cats[cat_name] = item
        return self.cats[cat_name]

    def adicionar_objeto_lista(self, nome: str, categoria: str, cor=None):
        parent = self._get_or_create_category(categoria)
        item = QtWidgets.QTreeWidgetItem(parent)
        item.setText(0, nome)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, QtCore.Qt.Checked)

        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(100)
        slider.setFixedHeight(14)
        slider.valueChanged.connect(lambda v: self.opacityChanged.emit(nome, v / 100.0))
        self.tree_widget.setItemWidget(item, 1, slider)

        btn_color = QtWidgets.QPushButton()
        btn_color.setFixedSize(14, 14)
        c = cor if cor else [1.0, 1.0, 1.0]
        color_hex = QtGui.QColor.fromRgbF(c[0], c[1], c[2]).name()
        btn_color.setStyleSheet(f"background-color: {color_hex}; border-radius: 7px; border: 1px solid #555;")
        btn_color.clicked.connect(lambda: self._pick_color(nome, btn_color))
        self.tree_widget.setItemWidget(item, 2, btn_color)

    def _show_context_menu(self, pos):
        item = self.tree_widget.itemAt(pos)
        if not item or not item.parent(): return

        menu = QtWidgets.QMenu()
        if menu.addAction("Excluir"):
            nome = item.text(0)
            self.deleteRequested.emit(nome)
            item.parent().removeChild(item)

    def _handle_item_changed(self, item, col):
        if col == 0:
            self.objetoToggled.emit(item.text(0), item.checkState(0) == QtCore.Qt.Checked)

    def _pick_color(self, name, btn):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            btn.setStyleSheet(f"background-color: {color.name()}; border-radius: 7px;")
            self.colorChanged.emit(name, color)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1200, 800)

        project_path = str(Path.home() / "OpenCMF_Projects" / "TestPatient")
        self.data_manager = ObjectManager(project_path)
        self.atores: Dict[str, vtk.vtkActor] = {}

        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.renderer.SetBackground(0.1, 0.1, 0.1)

        self.ui_manager = ObjetoManagerWidget()

        self.toolbar_comp = Component()
        self.addToolBar(self.toolbar_comp)

        central = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(central)
        layout.addWidget(self.ui_manager, 1)
        layout.addWidget(self.vtk_widget, 4)
        self.setCentralWidget(central)

        self._connect_logic()
        self.vtk_widget.Initialize()

    def _connect_logic(self):
        self.toolbar_comp.handler.importRequested.connect(self.solicitar_arquivo)
        self.data_manager.object_added.connect(self.carregar_na_cena)
        self.ui_manager.objetoToggled.connect(self.sync_vis)
        self.ui_manager.opacityChanged.connect(self.sync_opac)
        self.ui_manager.colorChanged.connect(self.sync_color)
        self.ui_manager.deleteRequested.connect(self.sync_del)

    def solicitar_arquivo(self, categoria, subcategoria):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Selecionar Malha", "", "Malhas (*.stl *.obj *.ply)"
        )
        if path:
            self.data_manager.import_object(path, categoria, subcategoria)

    def carregar_na_cena(self, props: ObjectProperties):
        full_path = self.data_manager.patient_path / props.file_path
        ext = Path(full_path).suffix.lower()

        readers = {".stl": vtk.vtkSTLReader, ".obj": vtk.vtkOBJReader, ".ply": vtk.vtkPLYReader}
        reader_cls = readers.get(ext)
        if not reader_cls: return

        reader = reader_cls()
        reader.SetFileName(str(full_path))
        reader.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        c = props.render["color"]
        actor.GetProperty().SetColor(c[0], c[1], c[2])

        self.renderer.AddActor(actor)
        self.atores[props.name] = actor
        self.ui_manager.adicionar_objeto_lista(props.name, props.type, c)

        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()

    def sync_vis(self, n, s):
        if n in self.atores:
            self.atores[n].SetVisibility(s)
            self.vtk_widget.GetRenderWindow().Render()

    def sync_opac(self, n, v):
        if n in self.atores:
            self.atores[n].GetProperty().SetOpacity(v)
            self.vtk_widget.GetRenderWindow().Render()

    def sync_color(self, n, c: QtGui.QColor):
        if n in self.atores:
            self.atores[n].GetProperty().SetColor(c.redF(), c.greenF(), c.blueF())
            self.vtk_widget.GetRenderWindow().Render()

    def sync_del(self, n):
        if n in self.atores:
            self.renderer.RemoveActor(self.atores.pop(n))
            self.vtk_widget.GetRenderWindow().Render()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())