'''
UI
 ↓
SceneManager
 ↓
EventBus
 ↓
Observers


class EventBus:
    def subscribe(self, event, callback):
        ...

    def unsubscribe(self, event, callback):
        ...

    def emit(self, event, **kwargs):
        ...

OBJECT_ADDED
OBJECT_REMOVED
OBJECT_UPDATED
SELECTION_CHANGED
VISIBILITY_CHANGED
'''