from typing import Dict, Optional, Any

class ActorRegistry:
    """
    Mantém o mapeamento entre o ID de um objeto de cena e seu respectivo ator visual.
    Responsabilidade: Apenas gestão de ciclo de vida de registros.
    """
    def __init__(self):
        self._actors: Dict[str, Any] = {}

    def register(self, obj_id: str, actor: Any):
        self._actors[obj_id] = actor

    def unregister(self, obj_id: str) -> Optional[Any]:
        # Retorna o ator removido, para que o chamador decida o que fazer com ele
        return self._actors.pop(obj_id, None)

    def get(self, obj_id: str) -> Optional[Any]:
        return self._actors.get(obj_id)

    def has(self, obj_id: str) -> bool:
        return obj_id in self._actors

    def replace(self, obj_id: str, actor: Any):
        # Apenas atualiza, mantendo o ID
        self._actors[obj_id] = actor

    def clear(self):
        self._actors.clear()