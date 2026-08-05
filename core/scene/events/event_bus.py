import logging
from collections import defaultdict
from typing import Callable, Any, Dict, List, Optional

logger = logging.getLogger("OpenCMF.EventBus")

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event: str, callback: Callable):
        if callback not in self._subscribers[event]:
            self._subscribers[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable):
        if event in self._subscribers:
            if callback in self._subscribers[event]:
                self._subscribers[event].remove(callback)

    def emit(self, event: str, **payload: Any):
        if event not in self._subscribers:
            return
        for callback in self._subscribers[event][:]:
            try:
                callback(**payload)
            except Exception as e:
                # Log do erro específico para facilitar debug (crucial no VTK/Qt)
                logger.error(f"Erro no evento '{event}' ao chamar {callback.__name__}: {e}", exc_info=True)

    def clear(self, event: Optional[str] = None):
        if event:
            self._subscribers.pop(event, None)
        else:
            self._subscribers.clear()