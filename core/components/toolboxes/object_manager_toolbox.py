import sys
import random
from pathlib import Path
from typing import Dict
from PySide6 import QtWidgets, QtCore, QtGui
import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class ObjetoManagerWidget(QtWidgets.QWidget):
    objetoToggled = QtCore.Signal(str, bool)
    opacityChanged = QtCore.Signal(str, float)
    colorChanged = QtCore.Signal(str, QtGui.QColor)
    deleteRequested = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cats = {}
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
        layout.addWidget(self.tree_widget)

    def _get_or_create_category(self, cat_name):
        if cat_name not in self.cats:
            cat_item = QtWidgets.QTreeWidgetItem(self.tree_widget)
            cat_item.setText(0, cat_name)
            cat_item.setExpanded(True)
            cat_item.setBackground(0, QtGui.QColor(240, 240, 240, 40))
            cat_item.setFirstColumnSpanned(True)

            font = cat_item.font(0)
            font.setBold(True)
            cat_item.setFont(0, font)
            self.cats[cat_name] = cat_item
        return self.cats[cat_name]

    def adicionar_objeto_lista(self, nome, categoria="Superfícies", cor=None):
        parent = self._get_or_create_category(categoria)
        item = QtWidgets.QTreeWidgetItem(parent)
        item.setText(0, nome)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, QtCore.Qt.Checked)

        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(100)
        slider.setFixedHeight(16)
        slider.valueChanged.connect(lambda v: self.opacityChanged.emit(nome, v / 100.0))
        self.tree_widget.setItemWidget(item, 1, slider)

        btn_color = QtWidgets.QPushButton()
        btn_color.setFixedSize(16, 16)
        c = cor if cor else (0.3, 0.6, 1.0)
        color_hex = QtGui.QColor.fromRgbF(c[0], c[1], c[2]).name()
        btn_color.setStyleSheet(f"background-color: {color_hex}; border-radius: 8px; border: 1px solid #888;")
        btn_color.clicked.connect(lambda: self._pick_color(nome, btn_color))
        self.tree_widget.setItemWidget(item, 2, btn_color)

    def _show_context_menu(self, position):
        item = self.tree_widget.itemAt(position)
        if not item or item.parent() is None:
            return

        menu = QtWidgets.QMenu()
        action_del = menu.addAction("Excluir")
        if menu.exec(self.tree_widget.viewport().mapToGlobal(position)) == action_del:
            self.deleteRequested.emit(item.text(0))
            item.parent().removeChild(item)

    def _handle_item_changed(self, item, column):
        if column == 0:
            self.objetoToggled.emit(item.text(0), item.checkState(0) == QtCore.Qt.Checked)

    def _pick_color(self, name, button):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}; border-radius: 8px; border: 1px solid #888;")
            self.colorChanged.emit(name, color)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenCMF - Visualizador de Objetos")
        self.resize(1200, 800)

        self.pasta_paciente = Path("./teste_registro_standalone/STL")
        self.pasta_paciente.mkdir(parents=True, exist_ok=True)

        self.atores: Dict[str, vtk.vtkActor] = {}
        self._init_vtk()
        self._init_ui()
        self.atualizar_da_pasta()

    def _init_vtk(self):
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.renderer.SetBackground(0.05, 0.05, 0.1)
        self.vtk_widget.Initialize()

    def _init_ui(self):
        self.toolbox = QtWidgets.QToolBox()
        self.manager_widget = ObjetoManagerWidget()

        self.toolbox.addItem(self.manager_widget, "Gerenciador de Objetos")

        self.setCentralWidget(QtWidgets.QWidget())
        layout = QtWidgets.QHBoxLayout(self.centralWidget())
        layout.addWidget(self.toolbox, 1)
        layout.addWidget(self.vtk_widget, 4)

        self.manager_widget.objetoToggled.connect(self.toggle_actor)
        self.manager_widget.opacityChanged.connect(self.set_actor_opacity)
        self.manager_widget.colorChanged.connect(self.set_actor_color)
        self.manager_widget.deleteRequested.connect(self.remove_actor)

    def atualizar_da_pasta(self):
        arquivos = list(self.pasta_paciente.glob("*.stl")) + list(self.pasta_paciente.glob("*.obj"))
        for file_path in arquivos:
            if file_path.name not in self.atores:
                self._carregar_arquivo_vtk(file_path)
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()

    def _carregar_arquivo_vtk(self, file_path):
        ext = file_path.suffix.lower()
        reader = vtk.vtkSTLReader() if ext == '.stl' else vtk.vtkOBJReader()
        reader.SetFileName(str(file_path))
        reader.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        color = [random.random() for _ in range(3)]
        actor.GetProperty().SetColor(color)

        self.renderer.AddActor(actor)
        self.atores[file_path.name] = actor
        self.manager_widget.adicionar_objeto_lista(file_path.name, "Arquivos Locais", color)

    def toggle_actor(self, name, visible):
        if name in self.atores:
            self.atores[name].SetVisibility(visible)
            self.vtk_widget.GetRenderWindow().Render()

    def set_actor_opacity(self, name, value):
        if name in self.atores:
            self.atores[name].GetProperty().SetOpacity(value)
            self.vtk_widget.GetRenderWindow().Render()

    def set_actor_color(self, name, color):
        if name in self.atores:
            self.atores[name].GetProperty().SetColor(color.redF(), color.greenF(), color.blueF())
            self.vtk_widget.GetRenderWindow().Render()

    def remove_actor(self, name):
        actor = self.atores.pop(name, None)
        if actor:
            self.renderer.RemoveActor(actor)
            self.vtk_widget.GetRenderWindow().Render()


class Component(QtWidgets.QWidget):
    def __init__(self, modulo=None):
        super().__init__()
        self.modulo = modulo

        self.setWindowTitle("Lista de Objetos")
        self.setObjectName("object_manager_toolbox")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.toolbox = QtWidgets.QToolBox()
        self.manager = ObjetoManagerWidget()

        self.toolbox.addItem(self.manager, "Gerenciador")
        layout.addWidget(self.toolbox)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())