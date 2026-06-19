'''
selected_object
active_viewer
current_patient
scene_metadata
'''

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Set


@dataclass
class SceneState:
    """
    Mantém o estado atual da interface e da cena.
    Atua como a 'Fonte da Verdade' (Source of Truth) para o sistema.
    """
    selected_object_ids: List[str] = field(default_factory=list)
    active_viewer: Optional[str] = None
    current_patient: Optional[str] = None
    scene_metadata: Dict[str, Any] = field(default_factory=dict)

    # Opcional: Adicionado para rastrear qual ferramenta está ativa no momento
    active_tool_name: Optional[str] = None

    def select(self, obj_id: str, exclusive: bool = True):
        """Adiciona um ID à seleção, com opção de seleção exclusiva."""
        if exclusive:
            self.selected_object_ids = [obj_id]
        elif obj_id not in self.selected_object_ids:
            self.selected_object_ids.append(obj_id)

    def deselect(self, obj_id: str):
        """Remove um ID específico da seleção."""
        if obj_id in self.selected_object_ids:
            self.selected_object_ids.remove(obj_id)

    def clear_selection(self):
        """Limpa toda a seleção."""
        self.selected_object_ids = []

    def set_viewer(self, viewer_id: Optional[str]):
        self.active_viewer = viewer_id

    def set_patient(self, patient_id: Optional[str]):
        self.current_patient = patient_id

    def set_active_tool(self, tool_name: Optional[str]):
        self.active_tool_name = tool_name

    def set_metadata(self, key: str, value: Any):
        self.scene_metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self.scene_metadata.get(key, default)