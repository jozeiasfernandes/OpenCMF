import os
import sys
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore


class WindowsRegistrationMenu(QtWidgets.QMenu):
    def __init__(self, parent, view_widget, side: str):
        super().__init__(parent)
        self.view_widget = view_widget
        self.side = side
        self._build_menu()

    def _build_menu(self):
        self.act_frontal = QtGui.QAction("Definir como Frontal", self)

        base_dir = Path(__file__).parent.parent.parent.parent

        icon_path = base_dir / "appearance" / "icons" / "vistas" / "frontal.svg"

        if icon_path.exists():
            self.act_frontal.setIcon(QtGui.QIcon(str(icon_path)))
        else:
            print(f"Ícone não encontrado: {icon_path}")  # útil para debug
            self.act_frontal.setIcon(QtWidgets.QApplication.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_DialogYesButton
            ))

        self.act_frontal.setShortcut(QtGui.QKeySequence("1"))
        self.act_frontal.setShortcutVisibleInContextMenu(True)
        self.act_frontal.triggered.connect(self._handle_set_frontal)

        self.addAction(self.act_frontal)

    def _handle_set_frontal(self):
        try:
            camera = self.view_widget.renderer.GetActiveCamera()
            pos = camera.GetPosition()
            foc = camera.GetFocalPoint()
            view_up = camera.GetViewUp()

            parent = self.parent()
            if hasattr(parent, 'redefinir_orientacao_global'):
                parent.redefinir_orientacao_global(self.side, pos, foc, view_up)
            else:
                print("Aviso: método redefinir_orientacao_global não encontrado no parent")
        except Exception as e:
            print(f"Erro ao definir orientação frontal: {e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    main_window = QtWidgets.QMainWindow()
    main_window.setWindowTitle("Teste - WindowsRegistrationMenu")
    main_window.resize(800, 600)

    central = QtWidgets.QWidget()
    main_window.setCentralWidget(central)


    # Dummy para teste
    class DummyViewWidget:
        class Renderer:
            def GetActiveCamera(self):
                class Camera:
                    def GetPosition(self):
                        return (0, 0, 1)

                    def GetFocalPoint(self):
                        return (0, 0, 0)

                    def GetViewUp(self):
                        return (0, 1, 0)

                return Camera()

        def __init__(self):
            self.renderer = self.Renderer()  # melhor como instância


    dummy_view = DummyViewWidget()
    menu = WindowsRegistrationMenu(main_window, dummy_view, side="A")

    main_window.show()


    def show_context_menu(pos):
        menu.exec(main_window.mapToGlobal(pos))


    main_window.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
    main_window.customContextMenuRequested.connect(show_context_menu)

    print("Menu criado com sucesso! Clique com o botão direito na janela para testar.")
    sys.exit(app.exec())