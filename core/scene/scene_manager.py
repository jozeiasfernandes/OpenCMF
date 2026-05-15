from typing import Optional, List, Any
from .scene_object import SceneObject
from .scene_state import SceneState
from .events.event_bus import EventBus
from .events.scene_events import (
    OBJECT_ADDED,
    OBJECT_REMOVED,
    OBJECT_UPDATED,
    VISIBILITY_CHANGED,
    SELECTION_CHANGED,  # Adicionado para notificar UI
)
from .registry.object_registry import ObjectRegistry
from .registry.actor_registry import ActorRegistry
from .selection.selection_manager import SelectionManager


class SceneManager:
    def __init__(
            self,
            state: SceneState,
            event_bus: EventBus,
            object_registry: ObjectRegistry,
            actor_registry: ActorRegistry,
            selection_manager: SelectionManager,
    ):
        self.state = state
        self.events = event_bus
        self.objects = object_registry
        self.actors = actor_registry
        self.selection = selection_manager

    def add_object(self, obj: SceneObject):
        self.objects.register(obj)
        self.events.emit(
            OBJECT_ADDED,
            object_id=obj.id,
            obj=obj
        )
        self.sync_state()

    def remove_object(self, obj_id: str):
        if not self.objects.has(obj_id):
            return

        self.objects.unregister(obj_id)
        self.actors.unregister(obj_id)

        # Garante que a seleção seja limpa antes de remover
        if self.selection.is_selected(obj_id):
            self.selection.deselect(obj_id)
            self._sync_selection_to_state()

        self.events.emit(OBJECT_REMOVED, object_id=obj_id)
        self.sync_state()

    def select_object(self, obj_id: Optional[str], multi: bool = False):
        if obj_id:
            self.selection.select(obj_id, exclusive=not multi)
        else:
            self.selection.clear()

        self._sync_selection_to_state()

        # Importante: Notificar que a seleção mudou para o Scene Monitor e Visualizadores
        self.events.emit(
            SELECTION_CHANGED,
            selected_ids=self.state.selected_object_ids
        )

    def update_visibility(self, obj_id: str, visible: bool):
        obj = self.objects.get(obj_id)
        if obj and obj.visible != visible:
            obj.visible = visible
            self.events.emit(
                VISIBILITY_CHANGED,
                object_id=obj_id,
                visible=visible
            )

    def update_opacity(self, obj_id: str, opacity: float):
        obj = self.objects.get(obj_id)
        if obj:
            obj.opacity = opacity
            self._emit_update(obj_id, "opacity", opacity)

    def update_color(self, obj_id: str, color: Any):
        obj = self.objects.get(obj_id)
        if obj:
            obj.color = color
            self._emit_update(obj_id, "color", color)

    def update_transform(self, obj_id: str, transform_data: dict):
        obj = self.objects.get(obj_id)
        if obj:
            obj.transform = transform_data
            self._emit_update(obj_id, "transforms", transform_data)

    def _emit_update(self, obj_id: str, prop: str, value: Any):
        self.events.emit(
            OBJECT_UPDATED,
            object_id=obj_id,
            property=prop,
            value=value
        )

    def get_object(self, obj_id: str) -> Optional[SceneObject]:
        return self.objects.get(obj_id)

    def _sync_selection_to_state(self):
        """Privado: Mantém o SceneState sincronizado com o SelectionManager."""
        self.state.selected_object_ids = list(self.selection.get_selected())

    def sync_state(self):
        """Atualiza metadados globais da cena."""
        self.state.scene_metadata["object_count"] = self.objects.count()
        self.state.scene_metadata["last_update"] = str(id(self))  # Exemplo de timestamp/hash