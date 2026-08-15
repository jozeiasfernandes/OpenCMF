from typing import Protocol, runtime_checkable, Dict, Optional, Any
from PySide6 import QtWidgets

@runtime_checkable
class IModule(Protocol):

    @property
    def id(self) -> str:
        ...

    @property
    def nome(self) -> str:
        ...

    def get_toolbar(self) -> Optional[QtWidgets.QToolBar]:
        ...

    def get_central_area(self) -> QtWidgets.QWidget:
        ...

    def get_side_panel(self) -> Dict[str, QtWidgets.QWidget]:
        ...

    def inicializar(self, path_pacient: str) -> None:
        ...

    def cleanup(self) -> None:
        ...


@runtime_checkable
class IWorkspaceTab(Protocol):

    def get_widget(self) -> QtWidgets.QWidget:
        ...

    def get_title(self) -> str:
        ...