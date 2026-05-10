import sys
import logging
import random
import json
from pathlib import Path
from typing import Dict, Optional
from PySide6 import QtWidgets, QtCore, QtGui
import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from core.imports.models_import import ObjectProperties

logger = logging.getLogger("ObjectManagerWidget")


class ObjetoManagerWidget(QtWidgets.QWidget):
    objetoToggled = QtCore.Signal(str, bool)
    opacityChanged = QtCore.Signal(str, float)
    colorChanged = QtCore.Signal(str, QtGui.QColor)
    deleteRequested = QtCore.Signal(str)
    nomeAlterado = QtCore.Signal(str, str)

    def __init__(self, parent=None, patient_path: Optional[str] = None):
        super().__init__(parent)
        self.cats = {}
        self.objetos_mapeados = {}
        self.patient_path = Path(patient_path) if patient_path else None
        self.object_properties: Dict[str, ObjectProperties] = {}
        self._setup_ui()
        
        if self.patient_path:
            self.carregar_objetos_da_pasta()

    def set_patient_path(self, path: str) -> None:
        """Define o caminho do paciente e carrega os objetos."""
        self.patient_path = Path(path)
        self.carregar_objetos_da_pasta()

    def carregar_objetos_da_pasta(self) -> None:
        """Carrega todos os objetos da pasta do paciente a partir dos arquivos .json."""
        if not self.patient_path or not self.patient_path.exists():
            logger.warning(f"Caminho do paciente não existe: {self.patient_path}")
            return

        # Limpar lista atual
        self.tree_widget.clear()
        self.cats.clear()
        self.objetos_mapeados.clear()
        self.object_properties.clear()

        loaded_count = 0
        for json_file in self.patient_path.rglob("*.json"):
            if "project" in json_file.parts:
                continue
            
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    props = ObjectProperties.from_json(data)
                    
                    # Mapear tipo para categoria de exibição
                    categoria = self._mapear_tipo_para_categoria(props.type)
                    
                    # Adicionar à lista
                    self.adicionar_objeto_lista(
                        props.name,
                        categoria,
                        props.render["color"],
                        objeto_id=props.id
                    )
                    
                    # Armazenar propriedades
                    self.object_properties[props.id] = props
                    loaded_count += 1
                    
            except (json.JSONDecodeError, TypeError, ValueError) as error:
                logger.warning(f"Erro ao carregar objeto de {json_file}: {error}")
                continue

        logger.info(f"Objetos carregados da pasta: {loaded_count} para paciente {self.patient_path}")

    def _mapear_tipo_para_categoria(self, tipo: str) -> str:
        """Mapeia o tipo do arquivo para a categoria de exibição."""
        mapeamento = {
            "surfaces": "Superfícies",
            "photos": "Fotografias", 
            "volume": "Volume",
            "others": "Outros"
        }
        return mapeamento.get(tipo, "Outros")

    def salvar_alteracao_objeto(self, objeto_id: str) -> None:
        """Salva as alterações de um objeto no arquivo .json."""
        if objeto_id not in self.object_properties:
            logger.warning(f"Objeto {objeto_id} não encontrado para salvar")
            return

        props = self.object_properties[objeto_id]
        json_path = self.patient_path / props.file_path
        
        try:
            with open(json_path.with_suffix(".json"), "w", encoding="utf-8") as f:
                json.dump(props.to_json(), f, indent=4, ensure_ascii=False)
            logger.debug(f"Alterações salvas para objeto: {props.name}")
        except Exception as error:
            logger.error(f"Erro ao salvar alterações do objeto {props.name}: {error}")

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
        self.tree_widget.doubleClicked.connect(self._on_double_clicked)
        layout.addWidget(self.tree_widget)

    def _get_or_create_category(self, cat_name: str) -> QtWidgets.QTreeWidgetItem:
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

    def adicionar_objeto_lista(self, nome: str, categoria: str = "Superfícies", cor=None, objeto_id: str = None) -> None:
        parent = self._get_or_create_category(categoria)
        item = QtWidgets.QTreeWidgetItem(parent)
        item.setText(0, nome)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, QtCore.Qt.Checked)

        if objeto_id:
            self.objetos_mapeados[nome] = objeto_id
            item.setData(0, QtCore.Qt.UserRole, objeto_id)

        # Obter opacidade das propriedades se disponível
        opacity_value = 100
        if objeto_id and objeto_id in self.object_properties:
            opacity_value = int(self.object_properties[objeto_id].opacity * 100)

        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(opacity_value)
        slider.setFixedHeight(16)
        slider.valueChanged.connect(lambda v, n=nome: self._on_opacity_changed(n, v))
        self.tree_widget.setItemWidget(item, 1, slider)

        btn_color = QtWidgets.QPushButton()
        btn_color.setFixedSize(16, 16)
        c = cor if cor else (0.3, 0.6, 1.0)
        color_hex = QtGui.QColor.fromRgbF(c[0], c[1], c[2]).name()
        btn_color.setStyleSheet(f"background-color: {color_hex}; border-radius: 8px; border: 1px solid #888;")
        btn_color.clicked.connect(lambda _, n=nome, b=btn_color: self._pick_color(n, b))
        self.tree_widget.setItemWidget(item, 2, btn_color)

    def _on_opacity_changed(self, name: str, value: int) -> None:
        opacity_float = value / 100.0
        
        # Salvar alteração de opacidade
        objeto_id = self.objetos_mapeados.get(name)
        if objeto_id and objeto_id in self.object_properties:
            self.object_properties[objeto_id].opacity = opacity_float
            self.salvar_alteracao_objeto(objeto_id)
        
        self.opacityChanged.emit(name, opacity_float)

    def _show_context_menu(self, position: QtCore.QPoint) -> None:
        item = self.tree_widget.itemAt(position)
        if not item or item.parent() is None:
            return

        menu = QtWidgets.QMenu()
        action_del = menu.addAction("Excluir")
        if menu.exec(self.tree_widget.viewport().mapToGlobal(position)) == action_del:
            nome_objeto = item.text(0)
            self.deleteRequested.emit(nome_objeto)
            item.parent().removeChild(item)
            logger.info(f"Objeto deletado: {nome_objeto}")

    def _handle_item_changed(self, item: QtWidgets.QTreeWidgetItem, column: int) -> None:
        if column == 0:
            self.objetoToggled.emit(item.text(0), item.checkState(0) == QtCore.Qt.Checked)

    def _on_double_clicked(self, index: QtCore.QModelIndex) -> None:
        item = self.tree_widget.itemFromIndex(index)
        if not item or item.parent() is None:
            return

        nome_original = item.text(0)
        objeto_id = item.data(0, QtCore.Qt.UserRole)
        
        novo_nome, ok = QtWidgets.QInputDialog.getText(
            self,
            "Renomear Objeto",
            f"Nome atual: {nome_original}",
            QtWidgets.QLineEdit.Normal,
            nome_original
        )

        if ok and novo_nome and novo_nome != nome_original:
            item.setText(0, novo_nome)
            
            # Atualizar propriedades e salvar
            if objeto_id and objeto_id in self.object_properties:
                self.object_properties[objeto_id].name = novo_nome
                self.salvar_alteracao_objeto(objeto_id)
            
            self.nomeAlterado.emit(nome_original, novo_nome)
            logger.info(f"Objeto renomeado: {nome_original} -> {novo_nome}")

    def _pick_color(self, name: str, button: QtWidgets.QPushButton) -> None:
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}; border-radius: 8px; border: 1px solid #888;")
            
            # Salvar alteração de cor
            objeto_id = self.objetos_mapeados.get(name)
            if objeto_id and objeto_id in self.object_properties:
                self.object_properties[objeto_id].render["color"] = [
                    color.redF(), color.greenF(), color.blueF()
                ]
                self.salvar_alteracao_objeto(objeto_id)
            
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
    toolbox_name = "Lista de Objetos"

    def __init__(self, modulo=None):
        super().__init__()
        self.modulo = modulo


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