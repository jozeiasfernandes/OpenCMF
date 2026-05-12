import sys
import json
import logging
import uuid
from pathlib import Path
from typing import Dict, Optional

from PySide6 import QtWidgets, QtCore, QtGui

from core.assets.models import ObjectProperties

logger = logging.getLogger("ObjectManagerWidget")

_TIPO_CAT = {
    "surfaces": "Superfícies",
    "photos": "Fotografias",
    "volume": "Volume",
    "others": "Outros",
}

_CAT_TIPO = {v: k for k, v in _TIPO_CAT.items()}


class ObjetoManagerWidget(QtWidgets.QWidget):
    objetoToggled = QtCore.Signal(str, bool)
    opacityChanged = QtCore.Signal(str, float)
    colorChanged = QtCore.Signal(str, QtGui.QColor)
    deleteRequested = QtCore.Signal(str)
    nomeAlterado = QtCore.Signal(str, str)
    objetoSelecionado = QtCore.Signal(str)
    requestSave = QtCore.Signal()

    def __init__(self, parent=None, patient_path: Optional[str] = None):
        super().__init__(parent)
        self.object_properties: Dict[str, ObjectProperties] = {}
        self._nome_para_id: Dict[str, str] = {}
        self.cats: Dict[str, QtWidgets.QTreeWidgetItem] = {}
        self.patient_path = Path(patient_path) if patient_path else None
        self._is_initializing = False
        self._setup_ui()

    def set_patient_path(self, path: str) -> None:
        self.patient_path = Path(path)

    def adicionar_objeto_lista(self, nome_ou_props=None, categoria="Superfícies", cor=None, objeto_id=None,
                               props=None) -> None:
        if props is None:
            props = nome_ou_props if isinstance(nome_ou_props, ObjectProperties) else None

        if props is None:
            oid = objeto_id or str(uuid.uuid4())
            props = ObjectProperties(
                id=oid,
                name=nome_ou_props or "Novo Objeto",
                type=_CAT_TIPO.get(categoria, "others")
            )
            if cor:
                props.render["color"] = [cor.redF(), cor.greenF(), cor.blueF()]

        self.object_properties[props.id] = props
        self._adicionar_item_arvore(props, categoria)

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderLabels(["Lista de Objetos", "Opacidade", "Cor"])
        self.tree_widget.setIndentation(12)
        self.tree_widget.setColumnWidth(1, 90)
        self.tree_widget.setColumnWidth(2, 32)

        self.tree_widget.itemClicked.connect(self._on_item_clicked)
        self.tree_widget.itemChanged.connect(self._handle_item_changed)
        self.tree_widget.doubleClicked.connect(self._on_double_clicked)
        self.tree_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.tree_widget)

    def _get_or_create_category(self, name: str) -> QtWidgets.QTreeWidgetItem:
        if name not in self.cats:
            it = QtWidgets.QTreeWidgetItem(self.tree_widget)
            it.setText(0, name)
            it.setExpanded(True)
            f = it.font(0)
            f.setBold(True)
            it.setFont(0, f)
            self.cats[name] = it
        return self.cats[name]

    def _adicionar_item_arvore(self, props: ObjectProperties, categoria: str) -> None:
        self._nome_para_id[props.name] = props.id
        cat_name = _TIPO_CAT.get(categoria, categoria)
        item = QtWidgets.QTreeWidgetItem(self._get_or_create_category(cat_name))
        item.setText(0, props.name)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, QtCore.Qt.Checked if props.visible else QtCore.Qt.Unchecked)
        item.setData(0, QtCore.Qt.UserRole, props.id)

        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(int(props.opacity * 100))
        slider.setMaximumHeight(14)
        slider.valueChanged.connect(lambda v, oid=props.id: self._on_opacity_changed(oid, v))
        self.tree_widget.setItemWidget(item, 1, slider)

        btn = QtWidgets.QPushButton()
        btn.setMaximumSize(14, 14)
        c = props.render.get("color", [1.0, 1.0, 1.0])
        btn.setStyleSheet(f"background-color: {QtGui.QColor.fromRgbF(c[0], c[1], c[2]).name()}; border-radius: 7px;")
        btn.clicked.connect(lambda _, oid=props.id, b=btn: self._pick_color(oid, b))
        self.tree_widget.setItemWidget(item, 2, btn)

    def _handle_item_changed(self, item, column):
        if column != 0 or item.parent() is None: return
        oid = item.data(0, QtCore.Qt.UserRole)
        if oid in self.object_properties:
            visivel = item.checkState(0) == QtCore.Qt.Checked
            self.object_properties[oid].visible = visivel
            self.objetoToggled.emit(oid, visivel)
            self.requestSave.emit()

    def _on_opacity_changed(self, oid, value):
        if oid in self.object_properties:
            self.object_properties[oid].opacity = value / 100.0
            self.opacityChanged.emit(oid, value / 100.0)
            self.requestSave.emit()

    def _pick_color(self, oid, btn):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            btn.setStyleSheet(f"background-color: {color.name()}; border-radius: 7px;")
            if oid in self.object_properties:
                self.object_properties[oid].render["color"] = [color.redF(), color.greenF(), color.blueF()]
                self.colorChanged.emit(oid, color)
                self.requestSave.emit()

    def _on_item_clicked(self, item, _col):
        if item.parent() is not None:
            oid = item.data(0, QtCore.Qt.UserRole)
            if oid: self.objetoSelecionado.emit(oid)

    def _on_double_clicked(self, index):
        item = self.tree_widget.itemFromIndex(index)
        if not item or item.parent() is None: return
        nome_antigo = item.text(0)
        oid = item.data(0, QtCore.Qt.UserRole)
        novo, ok = QtWidgets.QInputDialog.getText(self, "Renomear", "Novo nome:", text=nome_antigo)
        if ok and novo:
            item.setText(0, novo)
            self.object_properties[oid].name = novo
            self.nomeAlterado.emit(oid, novo)
            self.requestSave.emit()

    def _show_context_menu(self, pos):
        item = self.tree_widget.itemAt(pos)
        if not item or item.parent() is None: return
        menu = QtWidgets.QMenu()
        if menu.addAction("Excluir") == menu.exec(self.tree_widget.viewport().mapToGlobal(pos)):
            oid = item.data(0, QtCore.Qt.UserRole)
            self.deleteRequested.emit(oid)
            item.parent().removeChild(item)
            self.requestSave.emit()


class Component(QtWidgets.QWidget):
    toolbox_name = "Lista de Objetos"

    def __init__(self, modulo=None):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.manager = ObjetoManagerWidget()
        layout.addWidget(self.manager)
        if modulo:
            self.manager.requestSave.connect(
                lambda: modulo.patient_assets.save_scene() if hasattr(modulo, 'patient_assets') else None)
            # Vincular demais sinais...


if __name__ == "__main__":
    import sys
    from PySide6 import QtWidgets, QtCore, QtGui
    from core.scene.persistence.serializer import Serializer
    from core.assets.object_manager import ObjectManager

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    caminho_projeto_teste = r"C:\OpenCMF\patients\PRJ_1778357271_CELINE_DION"

    serializer = Serializer()
    obj_manager = ObjectManager(caminho_projeto_teste, serializer)

    obj_manager.load_patient_data()

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("OpenCMF - Teste de Gerenciador")
    window.resize(400, 600)

    lista_widget = ObjetoManagerWidget(patient_path=caminho_projeto_teste)

    for obj in obj_manager.objects.values():
        lista_widget.adicionar_objeto_lista(
            nome_ou_props=obj.name,
            categoria=obj.type,
            cor=QtGui.QColor.fromRgbF(obj.color[0], obj.color[1], obj.color[2]) if hasattr(obj, 'color') else None,
            objeto_id=obj.id
        )

    window.setCentralWidget(lista_widget)
    window.show()
    sys.exit(app.exec())