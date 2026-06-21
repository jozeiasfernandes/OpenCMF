from PySide6 import QtWidgets

class Component(QtWidgets.QToolBar):
    toolbar_name = "Nova_Toolbar"

    def __init__(self, modulo=None, scene_manager=None):
        super().__init__()
        self.setWindowTitle("Nova_Toolbar")
        self.setObjectName("nova_toolbar")
