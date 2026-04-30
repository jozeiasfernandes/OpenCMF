import sys
import random
from pathlib import Path
from typing import Optional, Dict

from PySide6 import QtWidgets, QtCore, QtGui
import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class ObjetoManagerWidget(QtWidgets.QWidget):
    objetoToggled = QtCore.Signal(str, bool)
    requestRefresh = QtCore.Signal()
    opacityChanged = QtCore.Signal(str, float)
    colorChanged = QtCore.Signal(str, QtGui.QColor)
    deleteRequested = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cats: Dict[str, QtWidgets.QTreeWidgetItem] = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderLabels(["Lista de Objetos", "Opacidade", "Cor"])
        self.tree_widget.setIndentation(15)
        self.tree_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self._show_context_menu)

        header = self.tree_widget.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        self.tree_widget.setColumnWidth(1, 100)
        self.tree_widget.setColumnWidth(2, 40)

        self.tree_widget.itemChanged.connect(self._handle_item_changed)
        layout.addWidget(QtWidgets.QLabel("<b>Object Manager:</b>"))
        layout.addWidget(self.tree_widget)

    def _get_or_create_category(self, cat_name: str):
        if cat_name not in self.cats:
            cat_item = QtWidgets.QTreeWidgetItem(self.tree_widget)
            cat_item.setText(0, cat_name)
            cat_item.setExpanded(True)

            bg_brush = QtGui.QBrush(QtGui.QColor(240, 240, 240, 40))
            cat_item.setBackground(0, bg_brush)
            cat_item.setFirstColumnSpanned(True)

            font = cat_item.font(0)
            font.setBold(True)
            cat_item.setFont(0, font)

            self.cats[cat_name] = cat_item
        return self.cats[cat_name]

    def adicionar_objeto_lista(self, nome: str, categoria: str = "Superfícies", cor=None):
        parent = self._get_or_create_category(categoria)
        item = QtWidgets.QTreeWidgetItem(parent)
        item.setText(0, nome)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, QtCore.Qt.Checked)

        slider_container = QtWidgets.QWidget()
        slider_layout = QtWidgets.QHBoxLayout(slider_container)
        slider_layout.setContentsMargins(4, 0, 4, 0)
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(100)
        slider.setFixedHeight(16)
        slider.valueChanged.connect(lambda v: self.opacityChanged.emit(nome, v / 100.0))
        slider_layout.addWidget(slider)
        self.tree_widget.setItemWidget(item, 1, slider_container)

        btn_container = QtWidgets.QWidget()
        btn_layout = QtWidgets.QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(QtCore.Qt.AlignCenter)
        btn_color = QtWidgets.QPushButton()
        btn_color.setFixedSize(16, 16)

        c = cor if cor else (0.3, 0.6, 1.0)
        color_hex = QtGui.QColor.fromRgbF(c[0], c[1], c[2]).name()

        btn_color.setStyleSheet(f"background-color: {color_hex}; border-radius: 8px; border: 1px solid #888;")
        btn_color.clicked.connect(lambda: self._pick_color(nome, btn_color))
        btn_layout.addWidget(btn_color)
        self.tree_widget.setItemWidget(item, 2, btn_container)

    def _show_context_menu(self, position):
        item = self.tree_widget.itemAt(position)
        if item and item.parent():
            nome = item.text(0)
            menu = QtWidgets.QMenu()
            action_del = menu.addAction("Excluir")
            action_del.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon))

            if menu.exec_(self.tree_widget.viewport().mapToGlobal(position)) == action_del:
                self.deleteRequested.emit(nome)
                parent = item.parent()
                parent.removeChild(item)

                if parent.childCount() == 0:
                    cat_name = parent.text(0)
                    index = self.tree_widget.indexOfTopLevelItem(parent)
                    self.tree_widget.takeTopLevelItem(index)
                    if cat_name in self.cats:
                        del self.cats[cat_name]

    def _handle_item_changed(self, item, column):
        if column == 0:
            self.objetoToggled.emit(item.text(0), item.checkState(0) == QtCore.Qt.Checked)

    def _pick_color(self, name, button):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}; border-radius: 8px; border: 1px solid #888;")
            self.colorChanged.emit(name, color)


class RegistrationToolbarHandler(QtCore.QObject):
    importRequested = QtCore.Signal()
    addPointToggled = QtCore.Signal(bool)
    deletePointRequested = QtCore.Signal()
    pointSizeChanged = QtCore.Signal(float)
    resetLayoutRequested = QtCore.Signal()

    def __init__(self, toolbar: QtWidgets.QToolBar):
        super().__init__()
        self.toolbar = toolbar
        self._setup_ui()

    def _setup_ui(self):
        style_btns = """
            QPushButton { 
                font-weight: bold; padding: 4px 12px; margin: 2px;
                background-color: #333; color: white; border-radius: 3px;
            }
            QPushButton:hover { background-color: #444; }
            QPushButton:checked { background-color: #0078d7; }
        """
        self.btn_import = QtWidgets.QPushButton("Import Objects")
        self.btn_import.setStyleSheet(style_btns)
        self.toolbar.addWidget(self.btn_import)

        self.btn_add = QtWidgets.QPushButton("Add Point")
        self.btn_add.setCheckable(True)
        self.btn_add.setStyleSheet(style_btns)
        self.toolbar.addWidget(self.btn_add)

        self.btn_del = QtWidgets.QPushButton("Delete Point")
        self.btn_del.setStyleSheet(style_btns)
        self.toolbar.addWidget(self.btn_del)

        self.btn_reset = QtWidgets.QPushButton("Reset View")
        self.btn_reset.setStyleSheet(style_btns)
        self.toolbar.addWidget(self.btn_reset)

        self.toolbar.addSeparator()

        self.slider_size = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_size.setRange(5, 50)
        self.slider_size.setValue(15)
        self.slider_size.setFixedWidth(80)

        self.toolbar.addWidget(QtWidgets.QLabel(" SIZE: "))
        self.toolbar.addWidget(self.slider_size)

        self.btn_import.clicked.connect(self.importRequested.emit)
        self.btn_add.toggled.connect(self.addPointToggled.emit)
        self.btn_del.clicked.connect(self.deletePointRequested.emit)
        self.btn_reset.clicked.connect(self.resetLayoutRequested.emit)
        self.slider_size.valueChanged.connect(lambda v: self.pointSizeChanged.emit(v / 10.0))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenCMF - Integrado")
        self.resize(1200, 800)

        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.renderer.SetBackground(0.05, 0.05, 0.1)
        self.atores: Dict[str, vtk.vtkActor] = {}

        toolbar_obj = QtWidgets.QToolBar()
        self.addToolBar(toolbar_obj)
        self.reg_handler = RegistrationToolbarHandler(toolbar_obj)

        self.manager = ObjetoManagerWidget()

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QHBoxLayout(central)
        layout.addWidget(self.manager, 1)
        layout.addWidget(self.vtk_widget, 4)

        self.reg_handler.importRequested.connect(self.importar_arquivos)
        self.manager.objetoToggled.connect(self.sync_vis)
        self.manager.opacityChanged.connect(self.sync_opac)
        self.manager.colorChanged.connect(self.sync_color)
        self.manager.deleteRequested.connect(self.sync_del)

        self.vtk_widget.Initialize()

    def importar_arquivos(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Importar Malhas", "", "STL Files (*.stl);;OBJ Files (*.obj)"
        )
        for f in files:
            path_obj = Path(f)
            name = path_obj.stem

            if name in self.atores:
                name = f"{name}_{random.randint(100, 999)}"

            color = [random.random() for _ in range(3)]

            if path_obj.suffix.lower() == '.stl':
                reader = vtk.vtkSTLReader()
            else:
                reader = vtk.vtkOBJReader()

            reader.SetFileName(f)
            reader.Update()

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(color)

            self.renderer.AddActor(actor)
            self.atores[name] = actor
            self.manager.adicionar_objeto_lista(name, "Importados", color)

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
            rgb = (c.redF(), c.greenF(), c.blueF())
            self.atores[n].GetProperty().SetColor(rgb)
            self.vtk_widget.GetRenderWindow().Render()

    def sync_del(self, n):
        if n in self.atores:
            actor = self.atores.pop(n)
            self.renderer.RemoveActor(actor)
            self.vtk_widget.GetRenderWindow().Render()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())