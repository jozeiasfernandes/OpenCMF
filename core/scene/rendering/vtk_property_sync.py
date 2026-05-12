'''
opacity
visibility
color
transform

UI
 ↓
SceneManager
 ↓
EventBus
 ↓
Renderer
 ↓
VTK

Nunca: UI → vtkActor

'''
from typing import Any, Optional
from ..scene_object import SceneObject


class VTKPropertySync:
    def __init__(self):
        self._cache = {}

    # -------------------------
    # Public API
    # -------------------------

    def sync(self, obj: SceneObject, actor: Any):
        if not obj or not actor:
            return

        self._sync_visibility(obj, actor)
        self._sync_opacity(obj, actor)
        self._sync_color(obj, actor)
        self._sync_transform(obj, actor)

    # -------------------------
    # Visibility
    # -------------------------

    def _sync_visibility(self, obj: SceneObject, actor: Any):
        actor.SetVisibility(bool(obj.visible))

    # -------------------------
    # Opacity
    # -------------------------

    def _sync_opacity(self, obj: SceneObject, actor: Any):
        prop = actor.GetProperty()
        if prop:
            prop.SetOpacity(float(obj.opacity))

    # -------------------------
    # Color
    # -------------------------

    def _sync_color(self, obj: SceneObject, actor: Any):
        prop = actor.GetProperty()
        if prop and obj.color:
            r, g, b = obj.color
            prop.SetColor(float(r), float(g), float(b))

    # -------------------------
    # Transform
    # -------------------------

    def _sync_transform(self, obj: SceneObject, actor: Any):
        t = obj.transform or {}

        position = t.get("position", [0.0, 0.0, 0.0])
        scale = t.get("scale", [1.0, 1.0, 1.0])
        rotation = t.get("rotation", [0.0, 0.0, 0.0])

        actor.SetPosition(*map(float, position))
        actor.SetScale(*map(float, scale))
        actor.SetOrientation(*map(float, rotation))

    def sync_all(self, obj: SceneObject, actor: Any):
        """Alias usado pela SceneBridge para reaplicar todo o estado do objeto no ator."""
        self.sync(obj, actor)

    def apply_property(self, actor: Any, property: str, value: Any):
        """Atualiza um único campo no ator (payload típico de OBJECT_UPDATED)."""
        if not actor or not property:
            return
        prop = actor.GetProperty()
        if property == "opacity" and prop:
            prop.SetOpacity(float(value))
            return
        if property == "color" and prop and value:
            r, g, b = value
            prop.SetColor(float(r), float(g), float(b))
            return
        if property == "transform" and isinstance(value, dict):
            position = value.get("position", [0.0, 0.0, 0.0])
            scale = value.get("scale", [1.0, 1.0, 1.0])
            rotation = value.get("rotation", [0.0, 0.0, 0.0])
            actor.SetPosition(*map(float, position))
            actor.SetScale(*map(float, scale))
            actor.SetOrientation(*map(float, rotation))