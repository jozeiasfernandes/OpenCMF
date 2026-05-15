from __future__ import annotations

from PySide6 import QtWidgets

from core.tools.base.tool_manager import ToolManager


class ViewportInteractionController:
    def __init__(
        self,
        vtk_widget,
        tool_manager: ToolManager,
    ):
        self.vtk_widget = vtk_widget
        self.tool_manager = tool_manager

        self.interactor = (
            vtk_widget
            .GetRenderWindow()
            .GetInteractor()
        )

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
        return self.interactor.GetEventPosition()

    @staticmethod
    def _get_modifiers():
        return QtWidgets.QApplication.keyboardModifiers()

    def _on_left_press(self, obj, event):
        x, y = self._get_mouse_position()

        handled = self.tool_manager.mouse_press(
            x=x,
            y=y,
            button="left",
            modifiers=self._get_modifiers(),
        )

        if not handled:
            obj.OnLeftButtonDown()

    def _on_left_release(self, obj, event):
        x, y = self._get_mouse_position()

        handled = self.tool_manager.mouse_release(
            x=x,
            y=y,
            button="left",
            modifiers=self._get_modifiers(),
        )

        if not handled:
            obj.OnLeftButtonUp()

    def _on_mouse_move(self, obj, event):
        x, y = self._get_mouse_position()

        handled = self.tool_manager.mouse_move(
            x=x,
            y=y,
            modifiers=self._get_modifiers(),
        )

        if not handled:
            obj.OnMouseMove()

    def _on_wheel_forward(self, obj, event):
        x, y = self._get_mouse_position()

        handled = self.tool_manager.wheel_forward(
            x=x,
            y=y,
            modifiers=self._get_modifiers(),
        )

        if not handled:
            obj.OnMouseWheelForward()

    def _on_wheel_backward(self, obj, event):
        x, y = self._get_mouse_position()

        handled = self.tool_manager.wheel_backward(
            x=x,
            y=y,
            modifiers=self._get_modifiers(),
        )

        if not handled:
            obj.OnMouseWheelBackward()

    def _on_key_press(self, obj, event):
        key = self.interactor.GetKeySym()

        handled = self.tool_manager.key_press(
            key=key,
            modifiers=self._get_modifiers(),
        )

        if not handled:
            obj.OnKeyPress()

    def _on_key_release(self, obj, event):
        key = self.interactor.GetKeySym()

        handled = self.tool_manager.key_release(
            key=key,
            modifiers=self._get_modifiers(),
        )

        if not handled:
            obj.OnKeyRelease()