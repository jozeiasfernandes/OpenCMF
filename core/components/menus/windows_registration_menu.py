from pathlib import Path
from core.components.bases.base_menu import BaseContextMenu

class WindowsRegistrationMenu(BaseContextMenu):
    def __init__(self, parent, view_widget, side: str):
        self.view_widget = view_widget
        self.side = side
        # O __init__ da BaseContextMenu já chama o setup_menu() automaticamente
        super().__init__(parent)

    def setup_menu(self):
        # Define o path do ícone
        base_dir = Path(__file__).parent.parent.parent.parent
        icon_path = base_dir / "appearance" / "icons" / "vistas" / "frontal.svg"

        # Utiliza o método utilitário da classe base_tool
        self.create_action(
            text="Definir como Frontal",
            callback=self._handle_set_frontal,
            icon_path=icon_path,
            shortcut="1"
        )

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
    import sys
    from PySide6 import QtWidgets, QtCore
    app = QtWidgets.QApplication(sys.argv)

    main_window = QtWidgets.QMainWindow()
    main_window.setWindowTitle("Teste - WindowsRegistrationMenu")
    main_window.resize(800, 600)


    # Dummy para teste
    class DummyViewWidget:
        class Renderer:
            def GetActiveCamera(self):
                class Camera:
                    def GetPosition(self): return (0, 0, 1)

                    def GetFocalPoint(self): return (0, 0, 0)

                    def GetViewUp(self): return (0, 1, 0)

                return Camera()

        def __init__(self):
            self.renderer = self.Renderer()


    dummy_view = DummyViewWidget()

    # Criamos o menu associado à janela principal
    menu = WindowsRegistrationMenu(main_window, dummy_view, side="A")

    # Definindo a política de menu de contexto da janela
    main_window.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

    # Conectando o evento ao método show_at_cursor da base_tool
    main_window.customContextMenuRequested.connect(lambda: menu.show_at_cursor())

    main_window.show()
    print("Menu criado com sucesso! Clique com o botão direito na janela para testar.")
    sys.exit(app.exec())