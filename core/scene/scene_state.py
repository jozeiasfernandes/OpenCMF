'''
selected_object
active_viewer
current_patient
scene_metadata
'''


from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class SceneState:
    selected_object_ids: List[str] = field(default_factory=list)

    active_viewer: Optional[str] = None
    current_patient: Optional[str] = None

    scene_metadata: Dict[str, Any] = field(default_factory=dict)

    def select(self, obj_id: str):
        if obj_id not in self.selected_object_ids:
            self.selected_object_ids.append(obj_id)

    def deselect(self, obj_id: str):
        if obj_id in self.selected_object_ids:
            self.selected_object_ids.remove(obj_id)

    def clear_selection(self):
        self.selected_object_ids.clear()

    def set_viewer(self, viewer_id: str):
        self.active_viewer = viewer_id

    def set_patient(self, patient_id: str):
        self.current_patient = patient_id

    def set_metadata(self, key: str, value: Any):
        self.scene_metadata[key] = value

    def get_metadata(self, key: str, default=None):
        return self.scene_metadata.get(key, default)