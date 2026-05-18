from PySide6.QtCore import Qt

# ==============================================================================
# GLOBAL SHORTCUTS (Application-Wide)
# ==============================================================================
GLOBAL_SHORTCUTS = {
    (Qt.ControlModifier, Qt.Key_O): "open",
    (Qt.ControlModifier, Qt.Key_S): "save",
    (Qt.ControlModifier, Qt.Key_W): "close_tab",
    (Qt.ControlModifier, Qt.Key_P): "print",

    Qt.Key_F11: "full",
    (Qt.ControlModifier, Qt.Key_L): "component_list",
    (Qt.ControlModifier, Qt.Key_H): "home",
}

# ==============================================================================
# 3D VIEW SHORTCUTS
# ==============================================================================
SHORTCUTS_3D = {
    # Camera
    Qt.Key_1: "frontal",
    Qt.Key_2: "right",
    Qt.Key_3: "left",
    Qt.Key_4: "superior",
    Qt.Key_5: "inferior",
    Qt.Key_O: "orthogonal",

    # Anatomy
    Qt.Key_M: "mandible",
    Qt.Key_N: "maxilla",
    Qt.Key_B: "skull",
    Qt.Key_V: "chin",

    # Tools
    Qt.Key_T: "translate",
    Qt.Key_E: "scale",
    Qt.Key_R: "rotate",
    Qt.Key_P: "pan",
    Qt.Key_Z: "zoom",

    # Actions
    (Qt.ControlModifier, Qt.Key_I): "import_objects",
    (Qt.ControlModifier, Qt.Key_Delete): "delete_object",
}

# ==============================================================================
# 2D MULTIPLANAR SHORTCUTS
# ==============================================================================
SHORTCUTS_2D = {
    # Orientations
    Qt.Key_A: "axial",
    Qt.Key_C: "coronal",
    Qt.Key_S: "sagittal",
    Qt.Key_D: "3d",

    # Tools
    (Qt.ControlModifier, Qt.Key_R): "ruler",
    (Qt.ControlModifier, Qt.Key_G): "guides",
}