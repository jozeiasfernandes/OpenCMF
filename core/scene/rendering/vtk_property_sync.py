'''
opacity
visibility
color
transforms

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
from typing import Any, Optional, Dict
from ..scene_object import SceneObject


class VTKPropertySync:
    """Sincroniza o estado do SceneObject com o vtkActor."""

    def sync(self, obj: SceneObject, actor: Any):
        if not obj or not actor:
            return

        actor.SetVisibility(bool(obj.visible))
        actor.SetPickable(bool(obj.selectable))

        self._sync_render_props(obj.render, actor)
        self._sync_transform(obj.transform, actor)

    def apply_property(self, actor: Any, property_name: str, value: Any):
        if not actor:
            return

        if property_name == "visible":
            actor.SetVisibility(bool(value))
        elif property_name == "opacity":
            actor.GetProperty().SetOpacity(float(value))
        elif property_name == "color":
            actor.GetProperty().SetColor(*map(float, value))
        elif property_name == "transforms":
            self._sync_transform(value, actor)
        elif property_name == "render":
            self._sync_render_props(value, actor)

    def _sync_render_props(self, render_dict: Dict[str, Any], actor: Any):
        prop = actor.GetProperty()
        if not prop:
            return

        if "color" in render_dict:
            prop.SetColor(*map(float, render_dict["color"]))

        prop.SetLighting(bool(render_dict.get("lighting", True)))
        prop.SetAmbient(float(render_dict.get("ambient", 0.1)))
        prop.SetDiffuse(float(render_dict.get("diffuse", 0.7)))
        prop.SetSpecular(float(render_dict.get("specular", 0.2)))
        prop.SetSpecularPower(float(render_dict.get("specular_power", 10.0)))

        repr_type = render_dict.get("representation", "surface")
        if repr_type == "wireframe":
            prop.SetRepresentationToWireframe()
        elif repr_type == "points":
            prop.SetRepresentationToPoints()
        else:
            prop.SetRepresentationToSurface()

        prop.SetEdgeVisibility(bool(render_dict.get("edge_visibility", False)))
        if "edge_color" in render_dict:
            prop.SetEdgeColor(*map(float, render_dict["edge_color"]))

    def _sync_transform(self, t: Dict[str, Any], actor: Any):
        if not t:
            return

        pos = t.get("position", [0.0, 0.0, 0.0])
        rot = t.get("rotation", [0.0, 0.0, 0.0])
        sca = t.get("scale", [1.0, 1.0, 1.0])

        actor.SetPosition(*map(float, pos))
        actor.SetOrientation(*map(float, rot))
        actor.SetScale(*map(float, sca))