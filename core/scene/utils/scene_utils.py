# core/scene/utils/scene_utils.py

from ..scene_object import SceneObject
from .id_generator import IDGenerator

class SceneUtils:
    @staticmethod
    def create_mesh_object(name: str, polydata, **kwargs) -> SceneObject:
        return SceneObject(
            id=IDGenerator.short(),
            name=name,
            type="mesh",
            data={"mesh": polydata},
            **kwargs
        )