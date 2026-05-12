# core/scene/scene_bridge.py
# core/scene/scene_bridge.py

from .events.event_bus import EventBus
from .events.scene_events import (
    OBJECT_ADDED,
    OBJECT_REMOVED,
    OBJECT_UPDATED,
    VISIBILITY_CHANGED,
)
from .registry.object_registry import ObjectRegistry
from .registry.actor_registry import ActorRegistry
from .rendering.vtk_actor_factory import VTKActorFactory
from .rendering.vtk_scene_renderer import VTKSceneRenderer
from .rendering.vtk_property_sync import VTKPropertySync


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
        self.events.subscribe(OBJECT_ADDED, self._on_object_added)
        self.events.subscribe(OBJECT_REMOVED, self._on_object_removed)
        self.events.subscribe(OBJECT_UPDATED, self._on_object_updated)
        self.events.subscribe(VISIBILITY_CHANGED, self._on_visibility_changed)

    def _on_object_added(self, object_id: str):
        obj = self.objects.get(object_id)
        if not obj:
            return

        actor = self.factory.create(obj)
        self.actors.register(object_id, actor)
        self.renderer.add_actor(object_id, actor)
        self.renderer.refresh()

    def _on_object_removed(self, object_id: str):
        self.renderer.remove_actor(object_id)
        self.renderer.refresh()

    def _on_object_updated(self, object_id: str, **kwargs):
        obj = self.objects.get(object_id)
        actor = self.actors.get(object_id)

        if obj and actor:
            self.sync.sync(obj, actor)
            self.renderer.refresh()

    def _on_visibility_changed(self, object_id: str, visible: bool):
        actor = self.actors.get(object_id)
        if actor:
            actor.SetVisibility(visible)
            self.renderer.refresh()