# core/workspace/__init__.py
from .manager import Manager
from .registry import WorkspaceRegistry
from .state import WorkspaceState
from .contracts import IModule, IWorkspaceTab

__all__ = ["Manager", "WorkspaceRegistry", "WorkspaceState", "IModule", "IWorkspaceTab"]