'''
3D Viewer
Axial Viewer
Sagittal Viewer
Coronal Viewer
Registration Viewer
'''


from typing import Dict, Optional, Any, List

class ViewerRegistry:
    """
    Mantém o registro dos visualizadores ativos (ex: Viewers VTK/Qt).
    Mapeia um ID de visualizador para sua instância correspondente.
    """
    def __init__(self):
        self._viewers: Dict[str, Any] = {}

    def register(self, viewer_id: str, viewer_instance: Any):
        """Registra um visualizador (ex: um widget de renderização)."""
        self._viewers[viewer_id] = viewer_instance

    def unregister(self, viewer_id: str) -> Optional[Any]:
        """Remove o visualizador e retorna a instância para limpeza."""
        return self._viewers.pop(viewer_id, None)

    def get(self, viewer_id: str) -> Optional[Any]:
        return self._viewers.get(viewer_id)

    def has(self, viewer_id: str) -> bool:
        return viewer_id in self._viewers

    def all_ids(self) -> List[str]:
        return list(self._viewers.keys())

    def clear(self):
        """Limpa todos os registros."""
        self._viewers.clear()