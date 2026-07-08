from typing import Any
from core.scene.scene_object import SceneObject


class VTKPropertySync:
    def sync(self, actor: Any, scene_object: SceneObject):
        self._sync_visibility(actor, scene_object)
        self._sync_transform(actor, scene_object)
        self._sync_render_props(actor, scene_object)

        if scene_object.type == "volume":
            self._sync_volume_props(actor, scene_object)

        is_selectable = scene_object.metadata.get("selectable", True)
        actor.SetPickable(bool(is_selectable))

    def apply_property(self, actor: Any, property_name: str, value: Any):
        if property_name == "threshold":
            pass

    def _sync_visibility(self, actor: Any, scene_object: SceneObject):
        actor.SetVisibility(int(scene_object.visible))
        prop = actor.GetProperty()
        prop.SetOpacity(scene_object.opacity)
        prop.SetColor(*scene_object.color)

    def _sync_transform(self, actor: Any, scene_object: SceneObject):
        transforms = scene_object.transforms
        actor.SetPosition(*transforms.get("position", [0.0, 0.0, 0.0]))
        actor.SetOrientation(*transforms.get("rotation", [0.0, 0.0, 0.0]))
        actor.SetScale(*transforms.get("scale", [1.0, 1.0, 1.0]))

    def _sync_render_props(self, actor: Any, scene_object: SceneObject):
        props = scene_object.render
        prop = actor.GetProperty()

        if "ambient" in props:
            prop.SetAmbient(props["ambient"])
        if "diffuse" in props:
            prop.SetDiffuse(props["diffuse"])
        if "specular" in props:
            prop.SetSpecular(props["specular"])

    def _sync_volume_props(self, actor: Any, scene_object: SceneObject):
        threshold = scene_object.volume.get("threshold")
        if threshold is not None:
            pass