import sys
import os
from typing import Any, Callable, List, Optional, Tuple, Dict

from PySide6 import QtWidgets, QtCore, QtGui

from core.scene.events.scene_events import (
    OBJECT_ADDED,
    OBJECT_REMOVED,
    OBJECT_UPDATED,
    VISIBILITY_CHANGED,
    SELECTION_CHANGED,
)

_TIPO_EXIBICAO = {
    "surfaces": "Superfícies",
    "photos": "Fotografias",
    "volume": "Volume",
    "models": "Modelos",
    "others": "Outros",
}


def _fase_para_objeto(obj: Any) -> str:
    md = getattr(obj, "metadata", None) or {}
    if isinstance(md, dict):
        g = md.get("group") or md.get("phase")
        if g: return str(g)
    t = getattr(obj, "type", None) or "generic"
    return _TIPO_EXIBICAO.get(t, str(t))


def _obter_tamanho_formatado(obj: Any) -> str:
    # Tenta obter do metadado 'size_bytes' ou calcula via sys.getsizeof
    md = getattr(obj, "metadata", None) or {}
    size = md.get("size_bytes")

    if size is None:
        size = sys.getsizeof(obj)

    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _obter_local_exato(obj: Any) -> str:
    md = getattr(obj, "metadata", None) or {}
    path = md.get("file_path") or md.get("origin")

    if path and os.path.exists(path):
        return path

    return str(md.get("storage", "RAM")).upper()


class Component(QtWidgets.QWidget):
    toolbox_name = "Monitor de Cena"
    itemSelected = QtCore.Signal(str)
    visibilityChanged = QtCore.Signal(str, bool)

    def __init__(self, modulo=None):
        super().__init__()
        self._modulo = modulo
        self._bound_bus = None
        self._callbacks: Optional[List[Tuple[str, Callable]]] = None
        self.setup_ui()
        self._bind_to_scene_manager()
        self.destroyed.connect(self._teardown_scene_bindings)

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)

        self._lbl_status = QtWidgets.QLabel("")
        self._lbl_status.setStyleSheet("color: #aaa; font-size: 11px;")
        self._lbl_status.hide()
        layout.addWidget(self._lbl_status)

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Nome", "Tipo / Grupo", "Tam.", "Local Exato"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # Otimização de espaço nas colunas técnicas
        header = self.tree.header()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Interactive)
        header.setDefaultSectionSize(150)

        self.tree.setStyleSheet("""
            QTreeWidget { background-color: #2b2b2b; color: #eee; border: 1px solid #3d3d3d; font-size: 11px; }
            QTreeWidget::item:selected { background-color: #3d3d3d; }
        """)

        self.tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.tree)

        self.btn_remove = QtWidgets.QPushButton("Remover da Cena")
        self.btn_remove.clicked.connect(self._solicitar_remocao)
        layout.addWidget(self.btn_remove)

    def showEvent(self, event: QtGui.QShowEvent):
        super().showEvent(event)
        self._bind_to_scene_manager()

    def _scene_manager(self):
        return getattr(self._modulo, "scene_manager", None) if self._modulo else None

    def _bind_to_scene_manager(self):
        sm = self._scene_manager()
        if not sm:
            self._lbl_status.setText("Inativo: scene_manager não encontrado.")
            self._lbl_status.show()
            self._teardown_scene_bindings()
            return

        self._lbl_status.hide()
        bus = sm.events
        if self._bound_bus is bus:
            self._refresh_from_scene()
            return

        self._teardown_scene_bindings()
        self._bound_bus = bus
        self._callbacks = [
            (OBJECT_ADDED, self._refresh_from_scene),
            (OBJECT_REMOVED, self._refresh_from_scene),
            (OBJECT_UPDATED, self._on_object_updated),
            (VISIBILITY_CHANGED, self._on_visibility_changed),
            (SELECTION_CHANGED, self._on_selection_changed),
        ]
        for ev, cb in self._callbacks:
            bus.subscribe(ev, cb)
        self._refresh_from_scene()

    def _teardown_scene_bindings(self):
        if self._bound_bus and self._callbacks:
            for ev, cb in self._callbacks:
                self._bound_bus.unsubscribe(ev, cb)
        self._bound_bus = None
        self._callbacks = None

    def _on_object_updated(self, **kwargs):
        props = {"name", "type", "visible", "opacity", "color", "transforms", "storage", "size_bytes"}
        if not kwargs.get("property") or kwargs.get("property") in props:
            self._refresh_from_scene()

    def _on_visibility_changed(self, object_id: str, visible: bool):
        self.visibilityChanged.emit(object_id, visible)
        self._refresh_from_scene()

    def _on_selection_changed(self, selected_ids: List[str] = None, **kwargs):
        ids = selected_ids or kwargs.get("selected_ids") or []
        if ids: self._highlight_selection(ids[0])

    def _highlight_selection(self, object_id: str):
        self.tree.blockSignals(True)
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.data(0, QtCore.Qt.UserRole) == object_id:
                self.tree.setCurrentItem(item)
                break
        self.tree.blockSignals(False)

    def _refresh_from_scene(self, **kwargs):
        sm = self._scene_manager()
        self.tree.blockSignals(True)

        prev_id = None
        if cur := self.tree.currentItem():
            prev_id = cur.data(0, QtCore.Qt.UserRole)

        self.tree.clear()
        if not sm:
            self.tree.blockSignals(False)
            return

        objs = sorted(sm.objects.all(), key=lambda o: (o.name or "").lower())
        for obj in objs:
            item = QtWidgets.QTreeWidgetItem([
                obj.name or obj.id,
                _fase_para_objeto(obj),
                _obter_tamanho_formatado(obj),
                _obter_local_exato(obj)
            ])
            item.setData(0, QtCore.Qt.UserRole, obj.id)
            item.setToolTip(3, item.text(3))  # Facilita ver caminhos longos

            cor = "#4CAF50" if obj.visible else "#888888"
            for col in range(4):
                item.setForeground(col, QtGui.QColor(cor))

            self.tree.addTopLevelItem(item)

        target = prev_id or (sm.selection.get_first_selected() if sm.selection else None)
        if target: self._highlight_selection(target)
        self.tree.blockSignals(False)

    def _on_item_clicked(self, item, column):
        oid = item.data(0, QtCore.Qt.UserRole) or item.text(0)
        self.itemSelected.emit(oid)
        if sm := self._scene_manager():
            sm.select_object(oid, multi=False)

    def _solicitar_remocao(self):
        if not (item := self.tree.currentItem()): return
        oid = item.data(0, QtCore.Qt.UserRole)
        self.itemSelected.emit(f"REMOVE:{oid}")

        om = getattr(self._modulo, "object_manager", None)
        if om and hasattr(om, "remove_object"):
            om.remove_object(oid)
        elif sm := self._scene_manager():
            sm.remove_object(oid)


if __name__ == "__main__":
    from core.scene.scene_object import SceneObject
    from core.scene.scene_state import SceneState
    from core.scene.scene_manager import SceneManager
    from core.scene.events.event_bus import EventBus
    from core.scene.registry.object_registry import ObjectRegistry
    from core.scene.registry.actor_registry import ActorRegistry
    from core.scene.selection.selection_manager import SelectionManager

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")


    class _Fake:
        def __init__(self):
            bus = EventBus()
            self.scene_manager = SceneManager(
                SceneState(), bus, ObjectRegistry(), ActorRegistry(),
                SelectionManager(event_bus=bus)
            )


    win = QtWidgets.QMainWindow()
    fake = _Fake()
    monitor = Component(modulo=fake)
    win.setCentralWidget(monitor)

    # Teste com dados técnicos simulados
    fake.scene_manager.add_object(SceneObject(
        id="1", name="Mandíbula", type="surfaces",
        metadata={"size_bytes": 15728640, "group": "segmentation", "file_path": "C:/Export/mandibula.stl"}
    ))
    fake.scene_manager.add_object(SceneObject(
        id="2", name="Tomo DICOM", type="volume",
        metadata={"size_bytes": 524288000, "storage": "DISCO", "origin": "/data/patient_01.vti"}
    ))

    win.show()
    sys.exit(app.exec())