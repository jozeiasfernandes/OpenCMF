import sys
import os
from typing import Any, List, Optional, Tuple
from PySide6 import QtWidgets, QtCore, QtGui

from core.scene.events.scene_events import SceneEvents
from core.components.bases.base_sidepanel import BaseSidePanel

_TIPO_EXIBICAO = {
    "surfaces": "Superfícies",
    "photos": "Fotografias",
    "volume": "Volume",
    "models": "Modelos",
    "others": "Outros",
}


class SceneMonitor_SidePanel(BaseSidePanel):
    side_panel_name = "Monitor de Cena"
    itemSelected = QtCore.Signal(str)
    visibilityChanged = QtCore.Signal(str, bool)

    def __init__(self, context=None, title="Monitor de Cena", parent=None):
        super().__init__(context=context, title=title, parent=parent)
        self._bind_to_scene_manager()

    def setup_ui(self) -> None:
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)

        self._lbl_status = QtWidgets.QLabel("")
        self._lbl_status.setStyleSheet("color: #aaa; font-size: 11px;")
        self.layout.addWidget(self._lbl_status)

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Nome", "Tipo / Grupo", "Tam.", "Local Exato"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tree.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        self.tree.itemClicked.connect(self._on_item_clicked)
        self.layout.addWidget(self.tree)

        self.btn_remove = QtWidgets.QPushButton("Remover da Cena")
        self.btn_remove.clicked.connect(self._solicitar_remocao)
        self.layout.addWidget(self.btn_remove)

    def _bind_to_scene_manager(self):
        if not self.has_scene:
            self._lbl_status.setText("Inativo: Nenhuma cena conectada.")
            self._lbl_status.show()
            return

        self._lbl_status.hide()

        if self.event_bus:
            self.event_bus.subscribe(SceneEvents.OBJECT_ADDED, self._refresh_from_scene)
            self.event_bus.subscribe(SceneEvents.OBJECT_REMOVED, self._refresh_from_scene)
            self.event_bus.subscribe(SceneEvents.OBJECT_UPDATED, self._on_object_updated)
            self.event_bus.subscribe(SceneEvents.VISIBILITY_CHANGED, self._on_visibility_changed)
            self.event_bus.subscribe(SceneEvents.SELECTION_CHANGED, self._on_selection_changed)

        self._refresh_from_scene()

    def _on_object_updated(self, object_id: str = None, **kwargs):
        self._refresh_from_scene()

    def _on_visibility_changed(self, object_id: str, visible: bool):
        self.visibilityChanged.emit(object_id, visible)
        self._refresh_from_scene()

    def _on_selection_changed(self, selected_ids: List[str] = None, **kwargs):
        ids = selected_ids or kwargs.get("selected_ids", [])
        if ids: self._highlight_selection(ids[0])

    def _highlight_selection(self, object_id: str):
        self.tree.blockSignals(True)
        items = self.tree.findItems(object_id, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive, 0)  # Simplificado
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.data(0, QtCore.Qt.UserRole) == object_id:
                self.tree.setCurrentItem(item)
        self.tree.blockSignals(False)

    def _refresh_from_scene(self, **kwargs):
        self.tree.blockSignals(True)
        current = self.tree.currentItem()
        prev_id = current.data(0, QtCore.Qt.UserRole) if current else None

        self.tree.clear()
        for obj in sorted(self.scene_manager.objects.all(), key=lambda o: (o.name or "").lower()):
            item = QtWidgets.QTreeWidgetItem([
                obj.name or obj.id, _fase_para_objeto(obj),
                _obter_tamanho_formatado(obj), _obter_local_exato(obj)
            ])
            item.setData(0, QtCore.Qt.UserRole, obj.id)
            for col in range(4): item.setForeground(col, QtGui.QColor("#4CAF50" if obj.visible else "#888888"))
            self.tree.addTopLevelItem(item)

        if prev_id: self._highlight_selection(prev_id)
        self.tree.blockSignals(False)

    def _on_item_clicked(self, item, column):
        oid = item.data(0, QtCore.Qt.UserRole)
        self.itemSelected.emit(oid)
        self.scene_manager.select_object(oid, multi=False)  # Uso correto do método [cite: 61]

    def _solicitar_remocao(self):
        if item := self.tree.currentItem():
            self.scene_manager.remove_object(item.data(0, QtCore.Qt.UserRole))  # Uso correto [cite: 60]

def _fase_para_objeto(obj: Any) -> str:
    md = getattr(obj, "metadata", None) or {}
    g = md.get("group") or md.get("phase")
    return str(g) if g else _TIPO_EXIBICAO.get(getattr(obj, "type", "generic"), str(obj.type))


def _obter_tamanho_formatado(obj: Any) -> str:
    md = getattr(obj, "metadata", None) or {}
    size = md.get("size_bytes", sys.getsizeof(obj))
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024: return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _obter_local_exato(obj: Any) -> str:
    md = getattr(obj, "metadata", None) or {}
    path = md.get("file_path") or md.get("origin")
    return path if (path and os.path.exists(path)) else str(md.get("storage", "RAM")).upper()

if __name__ == "__main__":
    from core.scene.scene_object import SceneObject
    from core.scene.scene_state import SceneState
    from core.scene.scene_manager import SceneManager
    from core.scene.events.event_bus import EventBus
    from core.scene.registry.object_registry import ObjectRegistry
    from core.scene.registry.actor_registry import ActorRegistry
    from core.scene.selection.selection_manager import SelectionManager
    from core.scene.io.importer import ObjectImporter

    app = QtWidgets.QApplication(sys.argv)
    bus = EventBus()

    # Instanciação necessária para o SceneManager
    sm = SceneManager(
        SceneState(), bus, ObjectRegistry(), ActorRegistry(),
        SelectionManager(SceneState(), bus), ObjectImporter(patient_path=".")
    )

    # CORREÇÃO: Passar os argumentos exigidos pela classe base (context e title)
    # A classe SceneMonitor_SidePanel deve ter sido ajustada no seu __init__
    # para aceitar esses parâmetros ou repassá-los ao super().
    win = SceneMonitor_SidePanel(context=sm, title="Monitor de Cena")
    win.show()
    sys.exit(app.exec())