import sys
import random
from pathlib import Path
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
        self.tree_widget.setHeaderLabels(["Lista de Objetos", "", ""])
        self.tree_widget.setIndentation(15)

        self.tree_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self._show_context_menu)

        header = self.tree_widget.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)

        self.tree_widget.setColumnWidth(1, 90)
        self.tree_widget.setColumnWidth(2, 35)

        self.tree_widget.itemChanged.connect(self._handle_item_changed)

        self.btn_refresh = QtWidgets.QPushButton(" Atualizar Lista")
        layout.addWidget(QtWidgets.QLabel("<b>Object Manager:</b>"))
        layout.addWidget(self.tree_widget)
        layout.addWidget(self.btn_refresh)

    def _get_or_create_category(self, cat_name):
        if cat_name not in self.cats:
            cat_item = QtWidgets.QTreeWidgetItem(self.tree_widget)
            cat_item.setText(0, cat_name)
            cat_item.setExpanded(True)
            color = QtGui.QColor("#ffffff")
            color.setAlpha(40)
            cat_item.setBackground(0, color)
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

        slider_container = QtWidgets.QWidget()
        slider_layout = QtWidgets.QHBoxLayout(slider_container)
        slider_layout.setContentsMargins(4, 0, 4, 0)

        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(100)
        slider.setFixedHeight(14)
        slider.valueChanged.connect(lambda v: self.opacityChanged.emit(nome, v / 100.0))
        slider_layout.addWidget(slider)

        self.tree_widget.setItemWidget(item, 1, slider_container)

        btn_container = QtWidgets.QWidget()
        btn_layout = QtWidgets.QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(QtCore.Qt.AlignCenter)

        btn_color = QtWidgets.QPushButton()
        btn_color.setFixedSize(14, 14)

        if cor:
            qcolor = QtGui.QColor.fromRgbF(cor[0], cor[1], cor[2])
            color_hex = qcolor.name()
        else:
            color_hex = "#55aaff"

        btn_color.setStyleSheet(f"background-color: {color_hex}; border-radius: 7px; border: 1px solid gray;")
        btn_color.clicked.connect(lambda: self._pick_color(nome, btn_color))
        btn_layout.addWidget(btn_color)

        self.tree_widget.setItemWidget(item, 2, btn_container)

    def _show_context_menu(self, position):
        item = self.tree_widget.itemAt(position)
        if item and item.parent():
            nome_objeto = item.text(0)
            menu = QtWidgets.QMenu()
            action_del = menu.addAction(f"Excluir")
            action_del.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon))

            action = menu.exec_(self.tree_widget.viewport().mapToGlobal(position))

            if action == action_del:
                self.deleteRequested.emit(nome_objeto)
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
            button.setStyleSheet(f"background-color: {color.name()}; border-radius: 7px; border: 1px solid gray;")
            self.colorChanged.emit(name, color)


class TestWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenCMF - Gestor de Objetos")
        self.resize(1100, 700)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)

        self.manager = ObjetoManagerWidget()
        main_layout.addWidget(self.manager, 1)

        self.vtk_widget = QVTKRenderWindowInteractor(self)
        main_layout.addWidget(self.vtk_widget, 2)

        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.renderer.SetBackground(0.05, 0.05, 0.1)

        self.atores = {}

        self.manager.objetoToggled.connect(self.toggle_actor)
        self.manager.opacityChanged.connect(self.set_actor_opacity)
        self.manager.colorChanged.connect(self.set_actor_color)
        self.manager.deleteRequested.connect(self.remove_actor)

        self._popular_cena_demonstracao()
        self.vtk_widget.Initialize()

    def _popular_cena_demonstracao(self):
        demo_data = [
            ("TC_ConeBeam_Paciente_01", vtk.vtkConeSource(), [0.8, 0.8, 0.8], "Volumes"),
            ("Mandibula_Segmento_Osteotomia_A", vtk.vtkSphereSource(), [1.0, 0.8, 0.6], "Superfícies"),
            ("Mandibula_Segmento_Osteotomia_B", vtk.vtkSphereSource(), [1.0, 0.7, 0.5], "Superfícies"),
            ("Maxila_Posicionamento_Final", vtk.vtkSphereSource(), [0.9, 0.9, 0.7], "Superfícies"),
            ("Foto_Frente_Total_Face_Neutral", vtk.vtkPlaneSource(), [1.0, 1.0, 1.0], "Fotografias"),
            ("Foto_Perfil_Direito_Sorriso", vtk.vtkPlaneSource(), [1.0, 1.0, 1.0], "Fotografias"),
            ("Guia_Cirurgico_Protendido_Superior", vtk.vtkCylinderSource(), [0.2, 0.6, 1.0], "Outros"),
            ("Plano_Oclusal_Referencia_Horizontal", vtk.vtkPlaneSource(), [1.0, 1.0, 0.0], "Outros")
        ]

        for nome, source, cor, cat in demo_data:
            self.criar_objeto_demo(nome, source, cor, cat)

    def criar_objeto_demo(self, nome, source, cor, cat):
        source.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(cor)
        actor.SetPosition(random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2))
        self.renderer.AddActor(actor)
        self.atores[nome] = actor
        self.manager.adicionar_objeto_lista(nome, cat, cor=cor)
        self.renderer.ResetCamera()

    def toggle_actor(self, nome, visivel):
        if nome in self.atores:
            self.atores[nome].SetVisibility(visivel)
            self.vtk_widget.GetRenderWindow().Render()

    def set_actor_opacity(self, nome, valor):
        if nome in self.atores:
            self.atores[nome].GetProperty().SetOpacity(valor)
            self.vtk_widget.GetRenderWindow().Render()

    def set_actor_color(self, nome, color):
        if nome in self.atores:
            r, g, b = color.getRgbF()[:3]
            self.atores[nome].GetProperty().SetColor(r, g, b)
            self.vtk_widget.GetRenderWindow().Render()

    def remove_actor(self, nome):
        if nome in self.atores:
            self.renderer.RemoveActor(self.atores[nome])
            del self.atores[nome]
            self.vtk_widget.GetRenderWindow().Render()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = TestWindow()
    win.show()
    sys.exit(app.exec())