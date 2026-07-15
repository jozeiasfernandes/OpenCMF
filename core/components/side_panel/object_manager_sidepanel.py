from typing import Dict, Optional, Any
import logging
import uuid
from pathlib import Path
from typing import Dict, Optional
from PySide6 import QtWidgets, QtCore, QtGui
from core.scene.scene_object import SceneObject
from core.scene.scene_manager import SceneManager
from core.components.bases.base_sidepanel import BaseSidePanel

logger = logging.getLogger("ObjectManagerWidget")

_TIPO_CAT = {
    "surfaces": "Superfícies",
    "photos": "Fotografias",
    "volume": "Volume",
    "others": "Outros",
}

_CAT_TIPO = {v: k for k, v in _TIPO_CAT.items()}


class ObjetoManagerWidget(BaseSidePanel):
    side_panel_name = "Gerenciador de Objetos"

    # Sinais
    objetoToggled = QtCore.Signal(str, bool)
    opacityChanged = QtCore.Signal(str, float)
    colorChanged = QtCore.Signal(str, tuple)
    deleteRequested = QtCore.Signal(str)
    nomeAlterado = QtCore.Signal(str, str)
    objetoSelecionado = QtCore.Signal(str)
    requestSave = QtCore.Signal()

    def __init__(self, context: Any, titulo: str = "Gerenciador de Objetos", parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(
            context=context,
            titulo=titulo,
            parent=parent
        )
        # O scene_manager já está disponível via self.scene_manager (propriedade da BaseSidePanel)
        self.cats: Dict[str, QtWidgets.QTreeWidgetItem] = {}
        self.setup_ui()

    @property
    def scene_manager(self):
        """Retorna o scene_manager do contexto."""
        return self._logic.scene_manager if hasattr(self, '_logic') else None

    def setup_ui(self) -> None:
        """Configura a interface do usuário."""
        # Limpar layout existente
        self.clear_layout(self.layout)

        # 1. Configuração do TreeWidget
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderLabels(["Objeto", "Opacidade", "Cor"])
        self.tree_widget.setIndentation(12)

        # Ajuste de colunas
        self.tree_widget.setColumnWidth(0, 150)
        self.tree_widget.setColumnWidth(1, 90)
        self.tree_widget.setColumnWidth(2, 32)

        # 2. Conexões de sinais
        self.tree_widget.itemClicked.connect(self._on_item_clicked)
        self.tree_widget.itemChanged.connect(self._handle_item_changed)
        self.tree_widget.doubleClicked.connect(self._on_double_clicked)

        # Context Menu
        self.tree_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self._show_context_menu)

        # 3. Adiciona ao layout
        self.layout.addWidget(self.tree_widget)

    def clear_layout(self, layout):
        """Remove todos os widgets de um layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def set_patient_path(self, path: str) -> None:
        self.patient_path = Path(path)

    def adicionar_objeto_lista(self, nome: str = "Novo Objeto", categoria: str = "others",
                               cor: Optional[tuple] = None, objeto_id: Optional[str] = None) -> None:
        if not self.scene_manager:
            logger.warning("SceneManager não disponível para adicionar objeto")
            return

        novo_obj = SceneObject(
            id=objeto_id or uuid.uuid4().hex[:12],
            name=nome,
            type=categoria
        )

        if cor:
            novo_obj.color = cor

        self.scene_manager.add_object(novo_obj)
        self._adicionar_item_arvore(novo_obj, categoria)

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

    def _adicionar_item_arvore(self, obj: SceneObject, categoria: str) -> None:
        if not self.tree_widget:
            return

        cat_name = _TIPO_CAT.get(obj.type, obj.type)
        item = QtWidgets.QTreeWidgetItem(self._get_or_create_category(cat_name))

        item.setText(0, obj.name)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, QtCore.Qt.Checked if obj.visible else QtCore.Qt.Unchecked)
        item.setData(0, QtCore.Qt.UserRole, obj.id)

        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(int(obj.opacity * 100))
        slider.setMaximumHeight(14)
        slider.valueChanged.connect(lambda v, oid=obj.id: self._on_opacity_changed(oid, v))
        self.tree_widget.setItemWidget(item, 1, slider)

        btn = QtWidgets.QPushButton()
        btn.setMaximumSize(14, 14)
        c = obj.color
        btn.setStyleSheet(f"background-color: {QtGui.QColor.fromRgbF(c[0], c[1], c[2]).name()}; border-radius: 7px;")
        btn.clicked.connect(lambda _, oid=obj.id, b=btn: self._pick_color(oid, b))
        self.tree_widget.setItemWidget(item, 2, btn)

    def _handle_item_changed(self, item, column):
        if column != 0 or item.parent() is None or not self.scene_manager:
            return

        oid = item.data(0, QtCore.Qt.UserRole)
        obj = self.scene_manager.objects.get(oid)

        if obj:
            visivel = item.checkState(0) == QtCore.Qt.Checked
            obj.visible = visivel

            from core.scene.events.scene_events import SceneEvents
            self.scene_manager.events.emit(
                SceneEvents.VISIBILITY_CHANGED,
                object_id=oid,
                visible=visivel
            )

    def _on_opacity_changed(self, oid, value):
        if not self.scene_manager:
            return
        obj = self.scene_manager.objects.get(oid)
        if obj:
            obj.opacity = value / 100.0
            self.opacityChanged.emit(oid, obj.opacity)

    def _pick_color(self, oid, btn):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            btn.setStyleSheet(f"background-color: {color.name()}; border-radius: 7px;")
            if not self.scene_manager:
                return
            obj = self.scene_manager.objects.get(oid)
            if obj:
                obj.color = (color.redF(), color.greenF(), color.blueF())
                self.colorChanged.emit(oid, obj.color)

    def _on_item_clicked(self, item, _col):
        if item.parent() is not None:
            oid = item.data(0, QtCore.Qt.UserRole)
            if oid:
                self.objetoSelecionado.emit(oid)

    def _on_double_clicked(self, index):
        item = self.tree_widget.itemFromIndex(index)
        if not item or item.parent() is None or not self.scene_manager:
            return
        oid = item.data(0, QtCore.Qt.UserRole)
        obj = self.scene_manager.objects.get(oid)
        if obj:
            novo, ok = QtWidgets.QInputDialog.getText(self, "Renomear", "Novo nome:", text=obj.name)
            if ok and novo:
                item.setText(0, novo)
                obj.name = novo
                self.nomeAlterado.emit(oid, novo)

    def _show_context_menu(self, pos):
        item = self.tree_widget.itemAt(pos)
        if not item or item.parent() is None or not self.scene_manager:
            return
        menu = QtWidgets.QMenu()
        action = menu.addAction("Excluir")
        if action == menu.exec(self.tree_widget.viewport().mapToGlobal(pos)):
            oid = item.data(0, QtCore.Qt.UserRole)
            self.deleteRequested.emit(oid)
            # Remove da árvore
            item.parent().removeChild(item)
            # Remove do SceneManager
            self.scene_manager.remove_object(oid)
            self.requestSave.emit()

    def remover_objeto_lista(self, object_id: str):
        """Remove um objeto da lista pelo ID."""
        if not self.tree_widget:
            return
        # Procurar o item na árvore
        for i in range(self.tree_widget.topLevelItemCount()):
            category_item = self.tree_widget.topLevelItem(i)
            for j in range(category_item.childCount()):
                child = category_item.child(j)
                if child.data(0, QtCore.Qt.UserRole) == object_id:
                    category_item.removeChild(child)
                    # Se a categoria ficou vazia, remover também
                    if category_item.childCount() == 0:
                        self.tree_widget.takeTopLevelItem(i)
                    return


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from core.scene.scene_state import SceneState
    from core.scene.events.event_bus import EventBus
    from core.scene.registry.object_registry import ObjectRegistry
    from core.scene.registry.actor_registry import ActorRegistry
    from core.scene.selection.selection_manager import SelectionManager
    from core.scene.io.importer import ObjectImporter
    from core.scene.utils.factory import SceneObjectFactory

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # 1. Definições iniciais de dependências
    caminho_projeto = r"C:\OpenCMF\patients\PRJ_1778357271_CELINE_DION"
    shared_state = SceneState()
    event_bus = EventBus()
    object_registry = ObjectRegistry()
    actor_registry = ActorRegistry()

    # 2. Instancia o SelectionManager e Importer
    selection_manager = SelectionManager(state=shared_state)
    importer = ObjectImporter(patient_path=caminho_projeto)

    # 3. Instancia o SceneManager
    scene_manager = SceneManager(
        state=shared_state,
        event_bus=event_bus,
        object_registry=object_registry,
        actor_registry=actor_registry,
        selection_manager=selection_manager,
        importer=importer
    )

    # 4. Carrega os dados
    base_path = Path(caminho_projeto)
    for cat in ["surfaces", "photos", "volume"]:
        cat_path = base_path / cat
        if cat_path.exists():
            for f in cat_path.glob("*"):
                if f.is_file():
                    obj = SceneObjectFactory.create_from_file(str(f), cat)
                    scene_manager.add_object(obj)

    # 5. Configura a UI
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("OpenCMF - Teste de Gerenciador")

    # CORRIGIDO: Usar a nova assinatura (context, titulo, parent)
    lista_widget = ObjetoManagerWidget(
        context=scene_manager,
        titulo="Gerenciador de Objetos",
        parent=None
    )

    # Popula a lista a partir do Registro do SceneManager
    for obj in scene_manager.objects.all():
        lista_widget._adicionar_item_arvore(obj, obj.type)

    window.setCentralWidget(lista_widget)
    window.show()
    sys.exit(app.exec())