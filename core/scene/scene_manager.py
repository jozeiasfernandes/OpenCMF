from typing import Optional, Any, List
from .scene_object import SceneObject
from .scene_state import SceneState
from .events.event_bus import EventBus
from .events.scene_events import SceneEvents
from .registry.object_registry import ObjectRegistry
from .registry.actor_registry import ActorRegistry
from .selection.selection_manager import SelectionManager
from .io.importer import ObjectImporter


class SceneManager:
    def __init__(
            self,
            state: SceneState,
            event_bus: EventBus,
            object_registry: ObjectRegistry,
            actor_registry: ActorRegistry,
            selection_manager: SelectionManager,
            importer: ObjectImporter,
            transform_manager: Any = None
    ):
        self.state = state
        self.events = event_bus
        self.objects = object_registry
        self.actors = actor_registry
        self.selection = selection_manager
        self.importer = importer
        self.transform_manager = transform_manager

    # ==================== Gerenciamento de Objetos ====================

    def add_object(self, obj: SceneObject) -> None:
        """Adiciona um objeto à cena."""
        if not obj or not obj.id:
            return
        self.objects.register(obj)
        self.events.emit(SceneEvents.OBJECT_ADDED, object_id=obj.id, obj=obj)

    def remove_object(self, obj_id: str) -> None:
        """Remove um objeto da cena."""
        obj = self.objects.get(obj_id)
        if not obj:
            return

        self.objects.unregister(obj_id)
        self.actors.unregister(obj_id)
        self.selection.deselect(obj_id)

        if hasattr(obj, 'file_path') and obj.file_path:
            self.importer.delete_physical_file(obj.file_path)

        self.events.emit(SceneEvents.OBJECT_REMOVED, object_id=obj_id)

    def get_object(self, obj_id: str) -> Optional[SceneObject]:
        """Retorna um objeto pelo ID."""
        return self.objects.get(obj_id)

    def get_objects(self) -> List[SceneObject]:
        """Retorna todos os objetos da cena."""
        return self.objects.all()

    def has_object(self, obj_id: str) -> bool:
        """Verifica se um objeto existe na cena."""
        return self.objects.has(obj_id)

    def count_objects(self) -> int:
        """Retorna o número de objetos na cena."""
        return self.objects.count()

    # ==================== Importação ====================

    def import_and_add(self, file_path: str, category: str) -> Optional[SceneObject]:
        """Importa um arquivo e adiciona à cena."""
        obj = self.importer.import_external_file(file_path, category)
        if obj:
            self.add_object(obj)
            return obj
        return None

    # ==================== Propriedades dos Objetos ====================

    def update_visibility(self, obj_id: str, visible: bool) -> None:
        """Atualiza a visibilidade de um objeto."""
        obj = self.objects.get(obj_id)
        if not obj:
            return
        obj.visible = visible
        self.events.emit(SceneEvents.VISIBILITY_CHANGED, object_id=obj_id, visible=visible)

    def update_opacity(self, obj_id: str, opacity: float) -> None:
        """Atualiza a opacidade de um objeto."""
        obj = self.objects.get(obj_id)
        if not obj:
            return
        obj.opacity = max(0.0, min(1.0, opacity))  # Clamp entre 0 e 1
        self.events.emit(SceneEvents.OBJECT_UPDATED, object_id=obj_id, property="opacity", value=obj.opacity)

    def update_color(self, obj_id: str, color: tuple) -> None:
        """Atualiza a cor de um objeto."""
        obj = self.objects.get(obj_id)
        if not obj:
            return
        # Garantir que a cor é uma tupla de 3 floats
        if len(color) == 3:
            obj.color = (float(color[0]), float(color[1]), float(color[2]))
        elif len(color) == 4:
            # Se for RGBA, ignorar o alpha
            obj.color = (float(color[0]), float(color[1]), float(color[2]))
        self.events.emit(SceneEvents.OBJECT_UPDATED, object_id=obj_id, property="color", value=obj.color)

    def update_position(self, obj_id: str, position: tuple) -> None:
        """Atualiza a posição de um objeto."""
        obj = self.objects.get(obj_id)
        if not obj:
            return
        if len(position) == 3:
            obj.position = (float(position[0]), float(position[1]), float(position[2]))
            self.events.emit(SceneEvents.OBJECT_UPDATED, object_id=obj_id, property="position", value=obj.position)

    def update_rotation(self, obj_id: str, rotation: tuple) -> None:
        """Atualiza a rotação de um objeto."""
        obj = self.objects.get(obj_id)
        if not obj:
            return
        if len(rotation) == 3:
            obj.rotation = (float(rotation[0]), float(rotation[1]), float(rotation[2]))
            self.events.emit(SceneEvents.OBJECT_UPDATED, object_id=obj_id, property="rotation", value=obj.rotation)

    def update_scale(self, obj_id: str, scale: tuple) -> None:
        """Atualiza a escala de um objeto."""
        obj = self.objects.get(obj_id)
        if not obj:
            return
        if len(scale) == 3:
            obj.scale = (float(scale[0]), float(scale[1]), float(scale[2]))
            self.events.emit(SceneEvents.OBJECT_UPDATED, object_id=obj_id, property="scale", value=obj.scale)

    def update_name(self, obj_id: str, name: str) -> None:
        """Atualiza o nome de um objeto."""
        obj = self.objects.get(obj_id)
        if not obj:
            return
        old_name = obj.name
        obj.name = name
        self.events.emit(SceneEvents.OBJECT_UPDATED, object_id=obj_id, property="name", value=name, old_value=old_name)

    # ==================== Seleção ====================

    def select_object(self, obj_id: Optional[str], multi: bool = False) -> None:
        """Seleciona um objeto."""
        if obj_id:
            self.selection.select(obj_id, exclusive=not multi)
        else:
            self.selection.clear()

    def deselect_object(self, obj_id: str) -> None:
        """Deseleciona um objeto."""
        self.selection.deselect(obj_id)

    def toggle_selection(self, obj_id: str) -> None:
        """Alterna a seleção de um objeto."""
        self.selection.toggle(obj_id)

    def get_selected_objects(self) -> List[str]:
        """Retorna os IDs dos objetos selecionados."""
        return self.selection.selected_ids

    def get_first_selected(self) -> Optional[str]:
        """Retorna o primeiro objeto selecionado."""
        return self.selection.get_first_selected()

    def clear_selection(self) -> None:
        """Limpa a seleção."""
        self.selection.clear()

    # ==================== Transformações ====================

    def apply_transform(self, obj_id: str, transform_matrix: Any) -> None:
        """Aplica uma transformação a um objeto."""
        if self.transform_manager:
            self.transform_manager.apply_transform(obj_id, transform_matrix)
            self.events.emit(SceneEvents.OBJECT_UPDATED, object_id=obj_id, property="transform")

    # ==================== Utilitários ====================

    def clear(self) -> None:
        """Remove todos os objetos da cena."""
        for obj in self.objects.all():
            self.remove_object(obj.id)

    def get_objects_by_type(self, obj_type: str) -> List[SceneObject]:
        """Retorna objetos filtrados por tipo."""
        return [obj for obj in self.objects.all() if obj.type == obj_type]