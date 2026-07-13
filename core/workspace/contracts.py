from typing import Protocol, runtime_checkable, Dict, Optional
from PySide6 import QtWidgets


@runtime_checkable
class IModule(Protocol):
    """
    Interface estendida para suportar a nova arquitetura de containers.
    """

    def get_main_widget(self) -> QtWidgets.QWidget: ...

    # Suporte explícito a Toolbars
    def get_workspace_toolbar(self) -> Optional[QtWidgets.QToolBar]: ...

    # Painéis laterais (Inspector)
    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]: ...

    def cleanup(self) -> None: ...


@runtime_checkable
class IWorkspaceTab(Protocol):
    def get_widget(self) -> QtWidgets.QWidget: ...

    def get_title(self) -> str: ...