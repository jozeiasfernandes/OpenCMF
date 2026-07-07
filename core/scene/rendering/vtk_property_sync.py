from typing import Any
from core.scene.scene_object import SceneObject

class VTKPropertySync:
    """Sincroniza o estado do SceneObject com o VTK Actor."""

    def sync(self, actor: Any, scene_object: SceneObject):
        """Sincroniza todas as propriedades de uma vez."""
        self._sync_visibility(actor, scene_object)
        self._sync_transform(actor, scene_object)
        self._sync_render_props(actor, scene_object)

        # Opcional: Se 'selectable' for uma regra de UI, pode ficar em 'metadata'
        is_selectable = scene_object.metadata.get("selectable", True)
        actor.SetPickable(bool(is_selectable))

    def _sync_visibility(self, actor: Any, scene_object: SceneObject):
        actor.SetVisibility(int(scene_object.visible))
        actor.GetProperty().SetOpacity(scene_object.opacity)
        actor.GetProperty().SetColor(*scene_object.color)

    def _sync_transform(self, actor: Any, scene_object: SceneObject):
        # Acesso ao dicionário unificado 'transforms'
        transforms = scene_object.transforms

        actor.SetPosition(*transforms.get("position", [0, 0, 0]))
        actor.SetOrientation(*transforms.get("rotation", [0, 0, 0]))
        actor.SetScale(*transforms.get("scale", [1, 1, 1]))

    def _sync_render_props(self, actor: Any, scene_object: SceneObject):
        # Acesso ao dicionário unificado 'render'
        props = scene_object.render
        property_obj = actor.GetProperty()

        # Exemplo de sincronização de propriedades de renderização
        if "ambient" in props:
            property_obj.SetAmbient(props["ambient"])
        if "diffuse" in props:
            property_obj.SetDiffuse(props["diffuse"])
        if "specular" in props:
            property_obj.SetSpecular(props["specular"])