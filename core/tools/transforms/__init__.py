'''
A partir dele:

* A janela não conhece mais ferramentas;
* Troca de modo vira troca de tool;
* Eventos do mouse/teclado são roteados;
* Futuras tools ficam plugáveis.

Responsabilidades:
ToolManager
 ├── registrar tools
 ├── ativar/desativar tool atual
 ├── encaminhar eventos
 ├── manter contexto
 └── expor tool ativa
'''


from __future__ import annotations

from typing import Dict, Optional, Type

from core.tools.base.base_tool import (
    BaseTool,
    InteractionContext,
)


class ToolManager:
    def __init__(self, context: InteractionContext):
        self.context = context

        self._tools: Dict[str, BaseTool] = {}

        self._active_tool: Optional[BaseTool] = None

    @property
    def active_tool(self) -> Optional[BaseTool]:
        return self._active_tool

    @property
    def active_tool_name(self) -> Optional[str]:
        if self._active_tool is None:
            return None

        return self._active_tool.name

    def register_tool(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def register_tool_class(
        self,
        tool_class: Type[BaseTool],
    ) -> None:
        tool = tool_class()

        self.register_tool(tool)

    def get_tool(
        self,
        tool_name: str,
    ) -> Optional[BaseTool]:
        return self._tools.get(tool_name)

    def set_active_tool(
        self,
        tool_name: str,
    ) -> bool:
        tool = self.get_tool(tool_name)

        if tool is None:
            return False

        if self._active_tool is tool:
            return True

        if self._active_tool is not None:
            self._active_tool.deactivate()

        self._active_tool = tool

        self._active_tool.activate(self.context)

        return True

    def clear_active_tool(self) -> None:
        if self._active_tool is not None:
            self._active_tool.deactivate()

        self._active_tool = None

    def mouse_press(
        self,
        x: int,
        y: int,
        button: str,
        modifiers=None,
    ) -> bool:
        if self._active_tool is None:
            return False

        return self._active_tool.mouse_press(
            x,
            y,
            button,
            modifiers,
        )

    def mouse_move(
        self,
        x: int,
        y: int,
        modifiers=None,
    ) -> bool:
        if self._active_tool is None:
            return False

        return self._active_tool.mouse_move(
            x,
            y,
            modifiers,
        )

    def mouse_release(
        self,
        x: int,
        y: int,
        button: str,
        modifiers=None,
    ) -> bool:
        if self._active_tool is None:
            return False

        return self._active_tool.mouse_release(
            x,
            y,
            button,
            modifiers,
        )

    def wheel_forward(
        self,
        x: int,
        y: int,
        modifiers=None,
    ) -> bool:
        if self._active_tool is None:
            return False

        return self._active_tool.wheel_forward(
            x,
            y,
            modifiers,
        )

    def wheel_backward(
        self,
        x: int,
        y: int,
        modifiers=None,
    ) -> bool:
        if self._active_tool is None:
            return False

        return self._active_tool.wheel_backward(
            x,
            y,
            modifiers,
        )

    def key_press(
        self,
        key: str,
        modifiers=None,
    ) -> bool:
        if self._active_tool is None:
            return False

        return self._active_tool.key_press(
            key,
            modifiers,
        )

    def key_release(
        self,
        key: str,
        modifiers=None,
    ) -> bool:
        if self._active_tool is None:
            return False

        return self._active_tool.key_release(
            key,
            modifiers,
        )

