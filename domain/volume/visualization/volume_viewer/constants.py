class VolumeViewerConstants:
    PLANES = ["Axial", "Sagittal", "Coronal"]
    DIM_MAP = {"Axial": 2, "Sagittal": 0, "Coronal": 1}
    NORMALS = {"Axial": (0, 0, 1), "Sagittal": (1, 0, 0), "Coronal": (0, 1, 0)}
    VIEW_UP = {"Axial": (0, -1, 0), "Sagittal": (0, 0, 1), "Coronal": (0, 0, 1)}
    COLORS = {"Axial": "#D32F2F", "Sagittal": "#FBC02D", "Coronal": "#388E3C", "3D": "#1976D2"}