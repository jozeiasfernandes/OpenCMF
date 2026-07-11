import os
import sys
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from PySide6 import QtWidgets, QtCore, QtGui
from core.components.central_area.base.base_central_area import CentralAreaBase

from core.scene.events.scene_events import SceneEvents, RegistrationEvents

os.environ["QT_API"] = "pyside6"

DISPLAY_TYPES = {
    "surfaces": "Superfícies",
    "photos": "Fotografias",
    "volume": "Volume",
    "models": "Modelos",
    "others": "Outros",
}

class SceneMonitorArea(CentralAreaBase):
    itemSelected = QtCore.Signal(object)

    def __init__(self, modulo=None):
        # Inicializa a base com título e cor de identificação
        super().__init__(titulo="Monitor de Cena", cor_identificacao="#90CAF9")
        self._modulo = modulo
        self._bound_bus = None
        self._callbacks = []
        self._group_items = {}
        self._object_items = {}

        self.vtkWidget.hide()


        self._setup_monitor_ui()
        self._bind_to_scene()

@dataclass
class RuntimeState:
    loaded: bool = True
    visible: bool = True
    selected: bool = False
    dirty: bool = False
    orphan: bool = False


def _get_object_group(obj: Any) -> str:
    metadata = getattr(obj, "metadata", {}) or {}
    group = metadata.get("group") or metadata.get("phase")
    if group:
        return str(group)

    obj_type = getattr(obj, "type", "generic")
    return DISPLAY_TYPES.get(obj_type, str(obj_type))


def _format_size(obj: Any) -> str:
    metadata = getattr(obj, "metadata", {}) or {}
    size = float(metadata.get("size_bytes", sys.getsizeof(obj)))

    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _get_storage_path(obj: Any) -> str:
    metadata = getattr(obj, "metadata", {}) or {}
    path = metadata.get("file_path") or metadata.get("origin")

    if path and os.path.exists(str(path)):
        return str(path)
    return str(metadata.get("storage", "RAM")).upper()


class SceneMonitorArea(CentralAreaBase):
    itemSelected = QtCore.Signal(object)

    def __init__(self, modulo=None):
        # Inicializa a base com título e cor de identificação
        super().__init__(titulo="Monitor de Cena", cor_identificacao="#90CAF9")
        self._modulo = modulo
        self._bound_bus = None
        self._callbacks = []
        self._group_items = {}
        self._object_items = {}

        # Substitui o espaço do VTK (ou o posiciona) pelo nosso monitor
        # Como o SceneMonitor não usa o renderizador VTK, removemos/escondemos o vtkWidget
        self.vtkWidget.hide()

        # Cria o layout de conteúdo principal dentro da área central
        self._setup_monitor_ui()
        self._bind_to_scene()

    def _setup_monitor_ui(self):
        # Container principal dentro do layout_principal da base
        self.container = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # Árvore de Objetos
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Nome", "Tipo", "Status", "Actors", "Memória", "Local"])
        self.tree.setStyleSheet("background: #2b2b2b; color: #eee; border: none;")

        # Inspector
        self.inspector = QtWidgets.QTreeWidget()
        self.inspector.setHeaderLabels(["Propriedade", "Valor"])
        self.inspector.setStyleSheet("background: #252526; color: #eee; border: none;")

        self.container.addWidget(self.tree)
        self.container.addWidget(self.inspector)

        # Adiciona ao layout original da classe base
        # Inserimos antes da barra inferior (índice 0)
        self.layout_principal.insertWidget(0, self.container)

        # Configurações de UI reaproveitadas do seu código original
        self.tree.itemClicked.connect(self._handle_item_click)
        self._setup_toolbar_controls()

    def _setup_toolbar_controls(self):
        """Adiciona controles específicos na barra inferior da CentralAreaBase"""
        btn_refresh = QtWidgets.QToolButton()
        btn_refresh.setText("↻")
        btn_refresh.clicked.connect(self._refresh_tree)
        self.adicionar_controle(btn_refresh)

    def _scene_manager(self):
        return getattr(self._modulo, "scene_manager", None)

    def _bind_to_scene(self):
        sm = self._scene_manager()
        if not sm or not hasattr(sm, "events"): return

        self._bound_bus = sm.events
        self._callbacks = [
            (OBJECT_ADDED, self._on_object_added),
            (OBJECT_REMOVED, self._on_object_removed),
            (OBJECT_UPDATED, self._on_object_updated),
            (VISIBILITY_CHANGED, self._on_visibility_changed),
            (SELECTION_CHANGED, self._on_selection_changed),
        ]

        for event, cb in self._callbacks:
            self._bound_bus.subscribe(event, cb)

        self._refresh_tree()

    def _teardown_scene(self):
        if self._bound_bus:
            for event, cb in self._callbacks:
                self._bound_bus.unsubscribe(event, cb)

    def _refresh_tree(self):
        sm = self._scene_manager()
        if not sm or not hasattr(sm, "objects"): return

        self.tree.clear()
        self._group_items.clear()
        self._object_items.clear()

        objects = sm.objects.all()
        if not objects: return

        for obj in sorted(objects, key=lambda x: (getattr(x, 'name', '') or "").lower()):
            self._create_or_update_item(obj)

    def _get_group(self, name):
        if name in self._group_items: return self._group_items[name]

        item = QtWidgets.QTreeWidgetItem([name])
        item.setFirstColumnSpanned(True)
        item.setFont(0, QtGui.QFont("Segoe UI", 9, QtGui.QFont.Bold))
        item.setForeground(0, QtGui.QColor("#90CAF9"))
        self.tree.addTopLevelItem(item)
        self._group_items[name] = item
        return item

    def _create_or_update_item(self, obj):
        if not hasattr(obj, 'id'): return

        runtime = self._get_runtime_state(obj)
        is_new = obj.id not in self._object_items

        if is_new:
            parent = self._get_group(_get_object_group(obj))
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, QtCore.Qt.UserRole, obj.id)
            self._object_items[obj.id] = item
        else:
            item = self._object_items[obj.id]

        item.setText(0, getattr(obj, 'name', obj.id) or obj.id)
        item.setText(1, getattr(obj, "type", "generic"))
        item.setText(2, self._state_to_text(runtime))
        item.setText(3, str(self._count_actors(obj.id)))
        item.setText(4, _format_size(obj))
        item.setText(5, _get_storage_path(obj))

        self._apply_style(item, runtime)
        self._update_actor_nodes(item, obj.id)

    def _get_runtime_state(self, obj) -> RuntimeState:
        sm = self._scene_manager()
        selected = False
        if hasattr(sm, "selection"):
            selection = sm.selection
            ids = getattr(selection, "selected_ids", [])
            if callable(ids): ids = ids()
            selected = obj.id in ids if isinstance(ids, (list, set, tuple)) else obj.id == ids

        return RuntimeState(
            visible=getattr(obj, "visible", True),
            selected=selected,
            orphan=self._count_actors(obj.id) == 0
        )

    def _state_to_text(self, state):
        flags = ["VISIBLE" if state.visible else "HIDDEN"]
        if state.selected: flags.append("SELECTED")
        if state.orphan: flags.append("ORPHAN")
        return " | ".join(flags)

    def _apply_style(self, item, state):
        color = "#42A5F5" if state.selected else (
            "#EF5350" if state.orphan else ("#4CAF50" if state.visible else "#757575"))
        brush = QtGui.QBrush(QtGui.QColor(color))
        for i in range(self.tree.columnCount()):
            item.setForeground(i, brush)

    def _count_actors(self, obj_id):
        return len(self._get_actors_safe(obj_id))

    def _get_actors_safe(self, obj_id) -> list:
        sm = self._scene_manager()
        if not sm or not hasattr(sm, "actors"): return []

        registry = sm.actors
        for method_name in ["get_actors_by_object", "get_by_object", "get"]:
            method = getattr(registry, method_name, None)
            if callable(method):
                try:
                    return method(obj_id) or []
                except:
                    continue
        return []

    def _update_actor_nodes(self, parent_item, obj_id):
        parent_item.takeChildren()
        actors = self._get_actors_safe(obj_id)

        for i, actor in enumerate(actors):
            child = QtWidgets.QTreeWidgetItem(parent_item, [f"Actor_{i}", type(actor).__name__, "RENDER"])
            child.setForeground(0, QtGui.QColor("#80CBC4"))

    def _populate_inspector(self, obj):
        self.inspector.clear()
        state = self._get_runtime_state(obj)

        sections = {
            "Objeto": {"Nome": getattr(obj, 'name', 'N/A'), "ID": obj.id, "Tipo": getattr(obj, "type", "gen")},
            "Transform": getattr(obj, "transforms", {}),
            "Status": {"Visible": state.visible, "Selected": state.selected, "Orphan": state.orphan}
        }

        for title, data in sections.items():
            root = QtWidgets.QTreeWidgetItem([title])
            root.setFont(0, QtGui.QFont("", -1, QtGui.QFont.Bold))
            self.inspector.addTopLevelItem(root)

            if isinstance(data, dict):
                for k, v in data.items():
                    QtWidgets.QTreeWidgetItem(root, [str(k), str(v)])
            root.setExpanded(True)

    def _on_object_added(self, object=None, **kwargs):
        obj = object or kwargs.get("object")
        if obj and not isinstance(obj, dict):
            self._create_or_update_item(obj)

    def _on_object_removed(self, object_id=None, **kwargs):
        oid = object_id or kwargs.get("object_id")
        if item := self._object_items.pop(oid, None):
            if parent := item.parent(): parent.removeChild(item)

    def _on_object_updated(self, object=None, **kwargs):
        obj = object or kwargs.get("object")
        if obj and not isinstance(obj, dict):
            self._create_or_update_item(obj)

    def _on_visibility_changed(self, object_id=None, **kwargs):
        oid = object_id or kwargs.get("object_id")
        sm = self._scene_manager()
        if sm and oid:
            if obj := sm.objects.get(oid): self._create_or_update_item(obj)

    def _on_selection_changed(self, selected_ids=None, **kwargs):
        ids = selected_ids or kwargs.get("selected_ids", [])
        sm = self._scene_manager()
        if not sm: return

        for obj_id, item in self._object_items.items():
            if obj := sm.objects.get(obj_id):
                self._create_or_update_item(obj)

        if ids and isinstance(ids, (list, tuple)):
            if obj := sm.objects.get(ids[0]):
                self._populate_inspector(obj)

    def _handle_item_click(self, item, _):
        obj_id = item.data(0, QtCore.Qt.UserRole)
        if not obj_id: return

        sm = self._scene_manager()
        if sm:
            if hasattr(sm, "select_object"):
                sm.select_object(obj_id)

            if obj := sm.objects.get(obj_id):
                self.itemSelected.emit(obj)
                self._populate_inspector(obj)


class Component(SceneMonitorCenter):
    toolbox_name = "Monitor de Cena"


if __name__ == "__main__":
    from core.scene.scene_object import SceneObject
    from core.scene.scene_state import SceneState
    from core.scene.scene_manager import SceneManager
    from core.scene.events.event_bus import EventBus
    from core.scene.registry.object_registry import (
        ObjectRegistry
    )
    from core.scene.registry.actor_registry import (
        ActorRegistry
    )
    from core.scene.selection.selection_manager import (
        SelectionManager
    )

    app = QtWidgets.QApplication(sys.argv)

    app.setStyle("Fusion")

    class _Fake:
        def __init__(self):
            bus = EventBus()

            self.scene_manager = SceneManager(
                SceneState(),
                bus,
                ObjectRegistry(),
                ActorRegistry(),
                SelectionManager(event_bus=bus),
            )

    window = QtWidgets.QMainWindow()

    fake = _Fake()

    central = SceneMonitorCenter(
        modulo=fake
    )

    window.setCentralWidget(central)

    fake.scene_manager.add_object(
        SceneObject(
            id="1",
            name="Mandíbula",
            type="surfaces",
            metadata={
                "size_bytes": 15728640,
                "group": "segmentation",
                "file_path": "C:/Export/mandibula.stl",
            },
        )
    )

    fake.scene_manager.add_object(
        SceneObject(
            id="2",
            name="Tomo DICOM",
            type="volume",
            metadata={
                "size_bytes": 524288000,
                "storage": "DISCO",
                "origin": "/data/patient_01.vti",
            },
        )
    )

    window.resize(1200, 700)

    window.show()

    sys.exit(app.exec())