import sys
import random
import os
import shutil
from pathlib import Path
from typing import Dict
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
            bg_color = QtGui.QColor(240, 240, 240, 40)
            cat_item.setBackground(0, bg_color)
            cat_item.setFirstColumnSpanned(True)
            font = cat_item.font(0)
            font.setBold(True)
            cat_item.setFont(0, font)
            self.cats[cat_name] = cat_item
        return self.cats[cat_name]

    def adicionar_objeto_lista(self, nome, categoria="Superfícies", cor=None):
        for i in range(self.tree_widget.topLevelItemCount()):
            cat = self.tree_widget.topLevelItem(i)
            for j in range(cat.childCount()):
                if cat.child(j).text(0) == nome:
                    return

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
        if not item or item.parent() is None:
            return
        nome_objeto = item.text(0)
        menu = QtWidgets.QMenu()
        action_del = menu.addAction("Excluir")
        action_del.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon))
        if menu.exec(self.tree_widget.viewport().mapToGlobal(position)) == action_del:
            parent = item.parent()
            self.deleteRequested.emit(nome_objeto)
            self.tree_widget.removeItemWidget(item, 1)
            self.tree_widget.removeItemWidget(item, 2)
            parent.removeChild(item)
            if parent.childCount() == 0:
                cat_name = parent.text(0)
                idx = self.tree_widget.indexOfTopLevelItem(parent)
                if idx != -1:
                    self.tree_widget.takeTopLevelItem(idx)
                    self.cats.pop(cat_name, None)

    def _handle_item_changed(self, item, column):
        if column == 0:
            try:
                self.objetoToggled.emit(item.text(0), item.checkState(0) == QtCore.Qt.Checked)
            except RuntimeError:
                pass

    def _pick_color(self, name, button):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}; border-radius: 8px; border: 1px solid #888;")
            self.colorChanged.emit(name, color)


class RegistrationToolbarHandler(QtCore.QObject):
    importRequested = QtCore.Signal()
    refreshRequested = QtCore.Signal()
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
            QPushButton { font-weight: bold; padding: 4px 12px; margin: 2px; background-color: #333; color: white; border-radius: 3px; }
            QPushButton:hover { background-color: #444; }
            QPushButton:checked { background-color: #0078d7; }
        """
        self.btn_import = QtWidgets.QPushButton("Import")
        self.btn_import.setStyleSheet(style_btns)
        self.toolbar.addWidget(self.btn_import)

        self.btn_refresh = QtWidgets.QPushButton("Atualizar")
        self.btn_refresh.setStyleSheet(style_btns)
        self.toolbar.addWidget(self.btn_refresh)

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
        self.btn_refresh.clicked.connect(self.refreshRequested.emit)
        self.btn_add.toggled.connect(self.addPointToggled.emit)
        self.btn_del.clicked.connect(self.deletePointRequested.emit)
        self.btn_reset.clicked.connect(self.resetLayoutRequested.emit)
        self.slider_size.valueChanged.connect(lambda v: self.pointSizeChanged.emit(v / 10.0))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenCMF - Integrado")
        self.resize(1200, 800)

        self.pasta_paciente = Path("./teste_registro_standalone/STL")
        self.pasta_paciente.mkdir(parents=True, exist_ok=True)

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

        self.reg_handler.importRequested.connect(self.importar_objetos)
        self.reg_handler.refreshRequested.connect(self.atualizar_da_pasta)
        self.manager.objetoToggled.connect(self.toggle_actor)
        self.manager.opacityChanged.connect(self.set_actor_opacity)
        self.manager.colorChanged.connect(self.set_actor_color)
        self.manager.deleteRequested.connect(self.remove_actor)

        self.vtk_widget.Initialize()
        self.atualizar_da_pasta()

    def atualizar_da_pasta(self):
        arquivos = list(self.pasta_paciente.glob("*.stl")) + list(self.pasta_paciente.glob("*.obj"))

        for file_path in arquivos:
            name = file_path.name
            if name not in self.atores:
                self._carregar_arquivo_vtk(file_path, name)

        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()

    def _carregar_arquivo_vtk(self, file_path, name):
        color = [random.random() for _ in range(3)]
        ext = file_path.suffix.lower()

        if ext == '.stl':
            reader = vtk.vtkSTLReader()
        elif ext == '.obj':
            reader = vtk.vtkOBJReader()
        else:
            return

        reader.SetFileName(str(file_path))
        reader.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)

        self.renderer.AddActor(actor)
        self.atores[name] = actor
        self.manager.adicionar_objeto_lista(name, "Arquivos Locais", color)

    def importar_objetos(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Selecionar Arquivos", "", "Malhas (*.stl *.obj)")
        for file_path in files:
            p = Path(file_path)
            dest = self.pasta_paciente / p.name
            if not dest.exists():
                shutil.copy(file_path, dest)

        self.atualizar_da_pasta()

    def toggle_actor(self, n, v):
        if n in self.atores:
            self.atores[n].SetVisibility(v)
            self.vtk_widget.GetRenderWindow().Render()

    def set_actor_opacity(self, n, v):
        if n in self.atores:
            self.atores[n].GetProperty().SetOpacity(v)
            self.vtk_widget.GetRenderWindow().Render()

    def set_actor_color(self, n, c):
        if n in self.atores:
            self.atores[n].GetProperty().SetColor(c.redF(), c.greenF(), c.blueF())
            self.vtk_widget.GetRenderWindow().Render()

    def remove_actor(self, n):
        actor = self.atores.pop(n, None)
        if actor:
            self.renderer.RemoveActor(actor)
            self.vtk_widget.GetRenderWindow().Render()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())