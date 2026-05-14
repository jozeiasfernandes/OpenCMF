import os
import sys
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from PySide6 import QtWidgets, QtCore, QtGui

from core.scene.events.scene_events import (
    OBJECT_ADDED,
    OBJECT_REMOVED,
    OBJECT_UPDATED,
    VISIBILITY_CHANGED,
    SELECTION_CHANGED,
)

os.environ["QT_API"] = "pyside6"

_TIPO_EXIBICAO = {
    "surfaces": "Superfícies",
    "photos": "Fotografias",
    "volume": "Volume",
    "models": "Modelos",
    "others": "Outros",
}


@dataclass
class RuntimeState:
    loaded: bool = True
    visible: bool = True
    selected: bool = False
    dirty: bool = False
    orphan: bool = False


def _fase_para_objeto(obj: Any) -> str:
    md = getattr(obj, "metadata", None) or {}

    if isinstance(md, dict):
        group = md.get("group") or md.get("phase")

        if group:
            return str(group)

    obj_type = getattr(obj, "type", None) or "generic"

    return _TIPO_EXIBICAO.get(obj_type, str(obj_type))


def _obter_tamanho_formatado(obj: Any) -> str:
    md = getattr(obj, "metadata", None) or {}

    size = md.get("size_bytes")

    if size is None:
        size = sys.getsizeof(obj)

    size = float(size)

    for unit in ["B", "KB", "MB", "GB"]:
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


class SceneMonitorCenter(QtWidgets.QWidget):
    itemSelected = QtCore.Signal(object)

    def __init__(self, modulo=None):
        super().__init__()

        self._modulo = modulo
        self._bound_bus = None
        self._callbacks: Optional[List[Tuple[str, Callable]]] = None

        self._group_items: Dict[str, QtWidgets.QTreeWidgetItem] = {}
        self._object_items: Dict[str, QtWidgets.QTreeWidgetItem] = {}

        self.setup_ui()
        self._bind_to_scene_manager()

        self.destroyed.connect(self._teardown_scene_bindings)

    def setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.header = QtWidgets.QFrame()

        self.header.setFixedHeight(38)

        self.header.setStyleSheet("""
            QFrame {
                background: #1f1f1f;
                border-bottom: 1px solid #3d3d3d;
            }
        """)

        self.header_layout = QtWidgets.QHBoxLayout(self.header)

        self.header_layout.setContentsMargins(12, 0, 12, 0)

        self.lbl_title = QtWidgets.QLabel("Scene monitor")

        self.lbl_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
        """)

        self.header_layout.addWidget(self.lbl_title)
        self.header_layout.addStretch()

        self.main_layout.addWidget(self.header)

        self.splitter_main = QtWidgets.QSplitter()

        self.main_layout.addWidget(self.splitter_main)

        self.left_panel = QtWidgets.QFrame()

        self.left_panel.setMinimumWidth(420)

        self.left_layout = QtWidgets.QVBoxLayout(self.left_panel)

        self.left_layout.setContentsMargins(4, 4, 4, 4)

        self.tree = QtWidgets.QTreeWidget()

        self.tree.setColumnCount(6)

        self.tree.setHeaderLabels([
            "Nome",
            "Tipo",
            "Status",
            "Actors",
            "Memória",
            "Local",
        ])

        self.tree.setAlternatingRowColors(True)
        self.tree.setUniformRowHeights(True)

        self.tree.setStyleSheet("""
            QTreeWidget {
                background: #2b2b2b;
                color: #eeeeee;
                border: 1px solid #3d3d3d;
                font-size: 11px;
            }

            QTreeWidget::item:selected {
                background: #404040;
            }
        """)

        header = self.tree.header()

        header.setSectionResizeMode(
            0,
            QtWidgets.QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            1,
            QtWidgets.QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            2,
            QtWidgets.QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            3,
            QtWidgets.QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            4,
            QtWidgets.QHeaderView.ResizeToContents
        )

        self.tree.itemClicked.connect(
            self._on_item_clicked
        )

        self.left_layout.addWidget(self.tree)

        self.splitter_main.addWidget(self.left_panel)

        self.inspector = QtWidgets.QTreeWidget()

        self.inspector.setMinimumWidth(350)

        self.inspector.setColumnCount(2)

        self.inspector.setHeaderLabels([
            "Propriedade",
            "Valor"
        ])

        self.inspector.setAlternatingRowColors(True)

        self.inspector.setStyleSheet("""
            QTreeWidget {
                background: #252526;
                color: #eeeeee;
                border: 1px solid #3d3d3d;
                font-size: 11px;
            }

            QTreeWidget::item:selected {
                background: #404040;
            }
        """)

        inspector_header = self.inspector.header()

        inspector_header.setSectionResizeMode(
            0,
            QtWidgets.QHeaderView.ResizeToContents
        )

        inspector_header.setSectionResizeMode(
            1,
            QtWidgets.QHeaderView.Stretch
        )

        self.splitter_main.addWidget(self.inspector)

        self.splitter_main.setStretchFactor(0, 2)
        self.splitter_main.setStretchFactor(1, 1)

    def _scene_manager(self):
        return getattr(self._modulo, "scene_manager", None)

    def _bind_to_scene_manager(self):
        sm = self._scene_manager()

        if not sm:
            return

        bus = getattr(sm, "events", None)

        if not bus:
            return

        if self._bound_bus is bus:
            return

        self._teardown_scene_bindings()

        self._bound_bus = bus

        self._callbacks = [
            (OBJECT_ADDED, self._on_object_added),
            (OBJECT_REMOVED, self._on_object_removed),
            (OBJECT_UPDATED, self._on_object_updated),
            (VISIBILITY_CHANGED, self._on_visibility_changed),
            (SELECTION_CHANGED, self._on_selection_changed),
        ]

        for event_name, callback in self._callbacks:
            bus.subscribe(event_name, callback)

        self._build_initial_tree()

    def _teardown_scene_bindings(self):
        if self._bound_bus and self._callbacks:
            for event_name, callback in self._callbacks:
                self._bound_bus.unsubscribe(
                    event_name,
                    callback
                )

        self._bound_bus = None
        self._callbacks = None

    def _build_initial_tree(self):
        sm = self._scene_manager()

        if not sm:
            return

        self.tree.clear()

        self._group_items.clear()
        self._object_items.clear()

        objects = sorted(
            sm.objects.all(),
            key=lambda obj: (obj.name or "").lower()
        )

        for obj in objects:
            self._create_object_item(obj)

    def _get_group_item(self, group_name):
        item = self._group_items.get(group_name)

        if item:
            return item

        item = QtWidgets.QTreeWidgetItem([group_name])

        item.setFirstColumnSpanned(True)

        font = item.font(0)

        font.setBold(True)

        item.setFont(0, font)

        brush = QtGui.QBrush(
            QtGui.QColor("#90CAF9")
        )

        for col in range(self.tree.columnCount()):
            item.setForeground(col, brush)

        self.tree.addTopLevelItem(item)

        self._group_items[group_name] = item

        return item

    def _create_object_item(self, obj):
        if obj.id in self._object_items:
            self._update_object_item(obj)
            return

        runtime = self._build_runtime_state(obj)

        parent_item = self._get_group_item(
            _fase_para_objeto(obj)
        )

        item = QtWidgets.QTreeWidgetItem([
            obj.name or obj.id,
            getattr(obj, "type", "generic"),
            self._runtime_to_text(runtime),
            str(self._get_actor_count(obj.id)),
            _obter_tamanho_formatado(obj),
            _obter_local_exato(obj),
        ])

        item.setData(
            0,
            QtCore.Qt.UserRole,
            obj.id
        )

        self._apply_runtime_visual(item, runtime)

        parent_item.addChild(item)

        self._object_items[obj.id] = item

        self._rebuild_actor_children(item, obj.id)

    def _rebuild_actor_children(self, parent_item, object_id):
        parent_item.takeChildren()

        actors = self._get_actors_by_object(object_id)

        for index, actor in enumerate(actors):
            actor_item = QtWidgets.QTreeWidgetItem([
                f"vtkActor_{index}",
                type(actor).__name__,
                "RENDER",
                "",
                "",
                "",
            ])

            brush = QtGui.QBrush(
                QtGui.QColor("#80CBC4")
            )

            for col in range(actor_item.columnCount()):
                actor_item.setForeground(col, brush)

            parent_item.addChild(actor_item)

    def _build_runtime_state(self, obj):
        sm = self._scene_manager()

        selection = getattr(sm, "selection", None)

        selected = False

        if selection:
            try:
                if hasattr(selection, "selected_ids"):
                    selected = obj.id in selection.selected_ids

                elif hasattr(selection, "get_selected_ids"):
                    selected = obj.id in selection.get_selected_ids()

                elif hasattr(selection, "get_selection"):
                    selected = obj.id in selection.get_selection()

                elif hasattr(selection, "get_first_selected"):
                    selected = (
                        obj.id ==
                        selection.get_first_selected()
                    )

            except Exception:
                selected = False

        return RuntimeState(
            loaded=True,
            visible=getattr(obj, "visible", True),
            selected=selected,
            dirty=False,
            orphan=self._is_orphan_object(obj.id),
        )

    @staticmethod
    def _runtime_to_text(runtime):
        flags = []

        flags.append(
            "VISIBLE"
            if runtime.visible
            else "HIDDEN"
        )

        if runtime.selected:
            flags.append("SELECTED")

        if runtime.dirty:
            flags.append("DIRTY")

        if runtime.orphan:
            flags.append("ORPHAN")

        return " | ".join(flags)

    @staticmethod
    def _apply_runtime_visual(item, runtime):
        color = "#4CAF50"

        if not runtime.visible:
            color = "#757575"

        if runtime.selected:
            color = "#42A5F5"

        if runtime.orphan:
            color = "#EF5350"

        brush = QtGui.QBrush(
            QtGui.QColor(color)
        )

        for col in range(item.columnCount()):
            item.setForeground(col, brush)

    def _get_actors_by_object(self, object_id):
        sm = self._scene_manager()

        if not sm:
            return []

        actor_registry = getattr(sm, "actors", None)

        if not actor_registry:
            return []

        if hasattr(actor_registry, "get_actors_by_object"):
            try:
                return (
                    actor_registry.get_actors_by_object(
                        object_id
                    ) or []
                )

            except Exception:
                return []

        return []

    def _get_actor_count(self, object_id):
        return len(
            self._get_actors_by_object(object_id)
        )

    def _is_orphan_object(self, object_id):
        return self._get_actor_count(object_id) == 0

    def _update_object_item(self, obj):
        item = self._object_items.get(obj.id)

        if not item:
            self._create_object_item(obj)
            return

        runtime = self._build_runtime_state(obj)

        item.setText(0, obj.name or obj.id)
        item.setText(1, getattr(obj, "type", "generic"))
        item.setText(2, self._runtime_to_text(runtime))
        item.setText(3, str(self._get_actor_count(obj.id)))
        item.setText(4, _obter_tamanho_formatado(obj))
        item.setText(5, _obter_local_exato(obj))

        self._apply_runtime_visual(item, runtime)

        self._rebuild_actor_children(item, obj.id)

    def _remove_object_item(self, object_id):
        item = self._object_items.pop(
            object_id,
            None
        )

        if not item:
            return

        parent = item.parent()

        if not parent:
            return

        index = parent.indexOfChild(item)

        if index >= 0:
            parent.takeChild(index)

    def _refresh_selection_visuals(self):
        sm = self._scene_manager()

        if not sm:
            return

        for object_id in self._object_items:
            obj = sm.objects.get(object_id)

            if obj:
                self._update_object_item(obj)

    def _highlight_selection(self, object_id):
        item = self._object_items.get(object_id)

        if not item:
            return

        self.tree.blockSignals(True)

        self.tree.setCurrentItem(item)

        self.tree.blockSignals(False)

    def _populate_inspector(self, obj):
        self.inspector.clear()

        runtime = self._build_runtime_state(obj)

        self._add_inspector_section(
            "Objeto",
            {
                "Nome": obj.name,
                "UUID": obj.id,
                "Tipo": getattr(obj, "type", "generic"),
                "Grupo": _fase_para_objeto(obj),
            }
        )

        transform = (
            getattr(obj, "transform", None)
            or {}
        )

        self._add_inspector_section(
            "Transform",
            {
                "Position": str(
                    transform.get(
                        "position",
                        [0, 0, 0]
                    )
                ),
                "Rotation": str(
                    transform.get(
                        "rotation",
                        [0, 0, 0]
                    )
                ),
                "Scale": str(
                    transform.get(
                        "scale",
                        [1, 1, 1]
                    )
                ),
            }
        )

        self._add_inspector_section(
            "Runtime",
            {
                "Visible": str(runtime.visible),
                "Selected": str(runtime.selected),
                "Dirty": str(runtime.dirty),
                "Orphan": str(runtime.orphan),
                "Actors": str(
                    self._get_actor_count(obj.id)
                ),
            }
        )

        self._populate_vtk_section(obj)

    def _add_inspector_section(self, title, data):
        root = QtWidgets.QTreeWidgetItem([title])

        font = root.font(0)

        font.setBold(True)

        root.setFont(0, font)

        self.inspector.addTopLevelItem(root)

        for key, value in data.items():
            child = QtWidgets.QTreeWidgetItem([
                str(key),
                str(value)
            ])

            root.addChild(child)

        root.setExpanded(True)

    def _populate_vtk_section(self, obj):
        actors = self._get_actors_by_object(obj.id)

        root = QtWidgets.QTreeWidgetItem(["VTK"])

        font = root.font(0)

        font.setBold(True)

        root.setFont(0, font)

        self.inspector.addTopLevelItem(root)

        for index, actor in enumerate(actors):
            actor_item = QtWidgets.QTreeWidgetItem([
                f"vtkActor_{index}",
                type(actor).__name__
            ])

            root.addChild(actor_item)

            mapper = None

            if hasattr(actor, "GetMapper"):
                mapper = actor.GetMapper()

            if mapper:
                mapper_item = QtWidgets.QTreeWidgetItem([
                    "Mapper",
                    type(mapper).__name__
                ])

                actor_item.addChild(mapper_item)

        root.setExpanded(True)

    def _on_object_added(self, object=None, **kwargs):
        if isinstance(object, dict):
            return

    def _on_object_removed(
        self,
        object_id=None,
        **kwargs
    ):
        if object_id:
            self._remove_object_item(object_id)

    def _on_object_updated(
        self,
        object=None,
        **kwargs
    ):
        if object:
            self._update_object_item(object)

    def _on_visibility_changed(
        self,
        object_id=None,
        **kwargs
    ):
        sm = self._scene_manager()

        if not sm or not object_id:
            return

        obj = sm.objects.get(object_id)

        if obj:
            self._update_object_item(obj)

    def _on_selection_changed(
        self,
        selected_ids=None,
        **kwargs
    ):
        self._refresh_selection_visuals()

        selected_ids = (
            selected_ids
            or kwargs.get("selected_ids")
            or []
        )

        if selected_ids:
            object_id = selected_ids[0]

            self._highlight_selection(object_id)

            sm = self._scene_manager()

            if sm:
                obj = sm.objects.get(object_id)

                if obj:
                    self._populate_inspector(obj)

    def _on_item_clicked(self, item, column):
        object_id = item.data(
            0,
            QtCore.Qt.UserRole
        )

        if not object_id:
            return

        self.itemSelected.emit(object_id)

        sm = self._scene_manager()

        if sm and hasattr(sm, "select_object"):
            sm.select_object(
                object_id,
                multi=False
            )

            obj = sm.objects.get(object_id)

            if obj:
                self._populate_inspector(obj)


class Component(SceneMonitorCenter):
    toolbox_name = "Monitor de Cena"

    def __init__(self, modulo=None):
        super().__init__(modulo=modulo)


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