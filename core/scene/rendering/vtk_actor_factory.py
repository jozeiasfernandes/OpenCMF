'''
SceneObject
   ↓
VTKActorFactory   ← AQUI acontece a conversão
   ↓
vtkActor
   ↓
ActorRegistry
   ↓
VTKSceneRenderer



SceneObject -> vtkActor

SceneObject → vtkActor (único lugar permitido)

✔ correto
✔ isolado
✔ reutilizável
✔ testável

Separação de responsabilidades interna:
Geometry
mesh → mapper → actor
Transform
position / rotation / scale
Properties
opacity
color
visibility

'''


from typing import Any
from ..scene_object import SceneObject


class VTKActorFactory:
    def __init__(self, vtk_module: Any):
        self._vtk = vtk_module

    def create(self, obj: SceneObject) -> Any:
        actor = self._vtk.vtkActor()

        self._apply_geometry(actor, obj)
        self._apply_transform(actor, obj)
        self._apply_properties(actor, obj)

        return actor

    def _apply_geometry(self, actor: Any, obj: SceneObject):
        mesh = obj.data.get("mesh")
        if not mesh:
            return

        mapper = self._vtk.vtkPolyDataMapper()
        mapper.SetInputData(mesh)
        actor.SetMapper(mapper)

    def _apply_transform(self, actor: Any, obj: SceneObject):
        t = obj.transform

        actor.SetPosition(*t.get("position", [0, 0, 0]))
        actor.SetScale(*t.get("scale", [1, 1, 1]))
        actor.SetOrientation(*t.get("rotation", [0, 0, 0]))

    def _apply_properties(self, actor: Any, obj: SceneObject):
        prop = actor.GetProperty()

        prop.SetOpacity(obj.opacity)
        prop.SetColor(*obj.color)
        actor.SetVisibility(obj.visible)