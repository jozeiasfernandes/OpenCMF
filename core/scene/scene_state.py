from dataclasses import dataclass, field
from typing import Optional, Set

@dataclass
class SceneState:
    """
    Estado da cena (Fonte da Verdade).
    Mantém apenas os dados atuais do estado da aplicação.
    Dados derivados ou metadados de persistência devem ser tratados
    fora deste estado de runtime.
    """
    selected_object_ids: Set[str] = field(default_factory=set)
    active_viewer: Optional[str] = None
    current_patient: Optional[str] = None
    active_tool_name: Optional[str] = None

