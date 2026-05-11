'''

UI / VTK / Tools
        ↓
SceneManager
        ↓
EventBus
        ↓
Observers (Renderer / Registry / UI adapters)
'''



from collections import defaultdict
from typing import Callable, Any, Dict, List, Optional


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[..., None]]] = defaultdict(list)

    # -------------------------
    # Subscription management
    # -------------------------

    def subscribe(self, event: str, callback: Callable[..., None]):
        if callback not in self._subscribers[event]:
            self._subscribers[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable[..., None]):
        if event in self._subscribers:
            if callback in self._subscribers[event]:
                self._subscribers[event].remove(callback)

    # -------------------------
    # Event emission
    # -------------------------

    def emit(self, event: str, **payload: Any):
        if event not in self._subscribers:
            return

        for callback in list(self._subscribers[event]):
            try:
                callback(**payload)
            except Exception:
                pass

    # -------------------------
    # Cleanup
    # -------------------------

    def clear(self, event: Optional[str] = None):
        if event:
            self._subscribers.pop(event, None)
        else:
            self._subscribers.clear()