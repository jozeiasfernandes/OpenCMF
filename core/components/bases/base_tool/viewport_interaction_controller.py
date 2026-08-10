from __future__ import annotations

from PySide6 import QtWidgets

from core.components.bases.base_tool.tool_manager import ToolManager


class ViewportInteractionController:
    def __init__(
        self,
        vtk_widget,
        tool_manager: ToolManager,
    ):
        self.vtk_widget = vtk_widget
        self.tool_manager = tool_manager

        render_window = vtk_widget.GetRenderWindow()
        self.interactor = render_window.GetInteractor() if render_window else None

        if self.interactor:
            self._bind_events()

    def _bind_events(self) -> None:
        self.interactor.AddObserver(
            "LeftButtonPressEvent",
            self._on_left_press,
        )

        self.interactor.AddObserver(
            "LeftButtonReleaseEvent",
            self._on_left_release,
        )

        self.interactor.AddObserver(
            "MouseMoveEvent",
            self._on_mouse_move,
        )

        self.interactor.AddObserver(
            "MouseWheelForwardEvent",
            self._on_wheel_forward,
        )

        self.interactor.AddObserver(
            "MouseWheelBackwardEvent",
            self._on_wheel_backward,
        )

        self.interactor.AddObserver(
            "KeyPressEvent",
            self._on_key_press,
        )

        self.interactor.AddObserver(
            "KeyReleaseEvent",
            self._on_key_release,
        )

    def _get_mouse_position(self):
        if not self.interactor:
            return (0, 0)
        return self.interactor.GetEventPosition()

    @staticmethod
    def _get_modifiers():
        return QtWidgets.QApplication.keyboardModifiers()

    def _delegate_to_style(self, interactor, method_name: str) -> None:
        """Delega a chamada de forma segura para o estilo de interação atual do VTK."""
        if hasattr(interactor, "GetInteractorStyle"):
            style = interactor.GetInteractorStyle()
            if style and hasattr(style, method_name):
                getattr(style, method_name)()

    def _on_left_press(self, obj, event):
        x, y = self._get_mouse_position()

        handled = self.tool_manager.mouse_press(
            x=x,
            y=y,
            button="left",
            modifiers=self._get_modifiers(),
        )

        if not handled:
            self._delegate_to_style(obj, "OnLeftButtonDown")

    def _on_left_release(self, obj, event):
        x, y = self._get_mouse_position()

        handled = self.tool_manager.mouse_release(
            x=x,
            y=y,
            button="left",
            modifiers=self._get_modifiers(),
        )

        if not handled:
            self._delegate_to_style(obj, "OnLeftButtonUp")

    def _on_mouse_move(self, obj, event):
        x, y = self._get_mouse_position()

        handled = False
        if hasattr(self.tool_manager, "mouse_move"):
            handled = self.tool_manager.mouse_move(
                x=x,
                y=y,
                modifiers=self._get_modifiers(),
            )

        if not handled:
            self._delegate_to_style(obj, "OnMouseMove")

    def _on_wheel_forward(self, obj, event):
        x, y = self._get_mouse_position()

        handled = self.tool_manager.wheel_forward(
            x=x,
            y=y,
            modifiers=self._get_modifiers(),
        )

        if not handled:
            self._delegate_to_style(obj, "OnMouseWheelForward")

    def _on_wheel_backward(self, obj, event):
        x, y = self._get_mouse_position()

        handled = self.tool_manager.wheel_backward(
            x=x,
            y=y,
            modifiers=self._get_modifiers(),
        )

        if not handled:
            self._delegate_to_style(obj, "OnMouseWheelBackward")

    def _on_key_press(self, obj, event):
        if not self.interactor:
            return
        key = self.interactor.GetKeySym()

        handled = self.tool_manager.key_press(
            key=key,
            modifiers=self._get_modifiers(),
        )

        if not handled:
            self._delegate_to_style(obj, "OnKeyPress")

    def _on_key_release(self, obj, event):
        if not self.interactor:
            return
        key = self.interactor.GetKeySym()

        handled = self.tool_manager.key_release(
            key=key,
            modifiers=self._get_modifiers(),
        )

        if not handled:
            self._delegate_to_style(obj, "OnKeyRelease")