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

    def create(self, scene_object: SceneObject) -> Any:
        actor = self._vtk.vtkActor()

        self._apply_geometry(actor, scene_object)
        self._apply_transform(actor, scene_object)
        self._apply_properties(actor, scene_object)

        return actor

    def _apply_geometry(self, actor: Any, scene_object: SceneObject):
        if not scene_object.mesh_data:
            return

        mapper = self._vtk.vtkPolyDataMapper()
        mapper.SetInputData(scene_object.mesh_data)
        actor.SetMapper(mapper)

    def _apply_transform(self, actor: Any, scene_object: SceneObject):
        transform = scene_object.transform

        actor.SetPosition(*transform["position"])
        actor.SetScale(*transform["scale"])
        actor.SetOrientation(*transform["rotation"])

    def _apply_properties(self, actor: Any, scene_object: SceneObject):
        properties = actor.GetProperty()

        properties.SetOpacity(scene_object.opacity)
        properties.SetColor(*scene_object.color)
        actor.SetVisibility(int(scene_object.visible))