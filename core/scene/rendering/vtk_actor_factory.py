from typing import Any
from core.scene.scene_object import SceneObject


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
        # Acessa os dados de malha via metadata (conforme definido na Factory)
        mesh_data = scene_object.metadata.get("mesh_data")

        if not mesh_data:
            return

        mapper = self._vtk.vtkPolyDataMapper()
        mapper.SetInputData(mesh_data)
        actor.SetMapper(mapper)

    def _apply_transform(self, actor: Any, scene_object: SceneObject):
        # Acessa o dicionário unificado 'transforms' (com 's')
        transforms = scene_object.transforms

        # Extrai os valores garantindo compatibilidade com o formato da dataclass
        pos = transforms.get("position", [0.0, 0.0, 0.0])
        rot = transforms.get("rotation", [0.0, 0.0, 0.0])
        scale = transforms.get("scale", [1.0, 1.0, 1.0])

        actor.SetPosition(*pos)
        actor.SetOrientation(*rot)
        actor.SetScale(*scale)

    def _apply_properties(self, actor: Any, scene_object: SceneObject):
        properties = actor.GetProperty()

        properties.SetOpacity(scene_object.opacity)
        properties.SetColor(*scene_object.color)
        actor.SetVisibility(int(scene_object.visible))