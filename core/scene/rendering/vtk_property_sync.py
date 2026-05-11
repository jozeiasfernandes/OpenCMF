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


from typing import Any
from ..scene_object import SceneObject


class VTKPropertySync:
    def __init__(self):
        self._cache = {}

    def sync(self, obj: SceneObject, actor: Any):
        self._sync_visibility(obj, actor)
        self._sync_opacity(obj, actor)
        self._sync_color(obj, actor)
        self._sync_transform(obj, actor)

    def _sync_visibility(self, obj: SceneObject, actor: Any):
        actor.SetVisibility(obj.visible)

    def _sync_opacity(self, obj: SceneObject, actor: Any):
        actor.GetProperty().SetOpacity(obj.opacity)

    def _sync_color(self, obj: SceneObject, actor: Any):
        actor.GetProperty().SetColor(*obj.color)

    def _sync_transform(self, obj: SceneObject, actor: Any):
        t = obj.transform

        actor.SetPosition(*t.get("position", [0, 0, 0]))
        actor.SetScale(*t.get("scale", [1, 1, 1]))
        actor.SetOrientation(*t.get("rotation", [0, 0, 0]))