import logging
from typing import Any

from core.scene.events.event_bus import EventBus
from core.scene.events.scene_events import SceneEvents
from core.scene.registry.actor_registry import ActorRegistry
from core.scene.registry.object_registry import ObjectRegistry
from core.scene.rendering.vtk_actor_factory import VTKActorFactory
from core.scene.rendering.vtk_property_sync import VTKPropertySync
from core.scene.rendering.vtk_scene_renderer import VTKSceneRenderer

logger = logging.getLogger("OpenCMF.SceneBridge")


class SceneBridge:
    def __init__(
            self,
            event_bus: EventBus,
            object_registry: ObjectRegistry,
            actor_registry: ActorRegistry,
            renderer: VTKSceneRenderer,
            factory: VTKActorFactory
    ):
        self.events = event_bus
        self.objects = object_registry
        self.actors = actor_registry
        self.renderer = renderer
        self.factory = factory
        self.sync = VTKPropertySync()

        self._setup_subscriptions()

    def _setup_subscriptions(self):
        self.events.subscribe(SceneEvents.OBJECT_ADDED, self._on_object_added)
        self.events.subscribe(SceneEvents.OBJECT_REMOVED, self._on_object_removed)
        self.events.subscribe(SceneEvents.OBJECT_UPDATED, self._on_object_updated)
        self.events.subscribe(SceneEvents.VISIBILITY_CHANGED, self._on_visibility_changed)

    def _on_object_added(self, object_id: str, obj=None):
        target_obj = obj or self.objects.get(object_id)

        if not target_obj or self.actors.has(object_id):
            return

        actor = self.factory.create(target_obj)
        self.actors.register(object_id, actor)

        self.renderer.add_actor(actor)
        self.renderer.refresh()

    def _on_object_removed(self, object_id: str):
        actor = self.actors.get(object_id) # Recupera o ator antes de unregister
        if actor:
            self.actors.unregister(object_id)
            self.renderer.remove_actor(actor) # Passa apenas o ator
            self.renderer.refresh()

    def _on_object_updated(self, object_id: str, property: str = None, value: Any = None):
        """
        Atualiza um ator na cena baseado em um evento de atualização.
        """
        actor = self.actors.get(object_id)

        if not actor:
            logger.debug(f"SceneBridge: Objeto '{object_id}' não encontrado nos atores ativos. Ignorando atualização.")
            return
        try:
            if property:
                self.sync.apply_property(actor, property, value)
            else:
                obj = self.objects.get(object_id)
                if obj:
                    self.sync.sync(actor, scene_object=obj)
                else:
                    logger.warning(
                        f"SceneBridge: Objeto '{object_id}' encontrado nos atores, mas ausente no registro de dados.")

        except Exception as e:
            logger.error(f"Erro ao sincronizar propriedades do objeto '{object_id}': {e}", exc_info=True)
            return
        self.renderer.refresh()

    def _on_visibility_changed(self, object_id: str, visible: bool):
        actor = self.actors.get(object_id)
        if actor:
            actor.SetVisibility(int(visible))
            self.renderer.refresh()