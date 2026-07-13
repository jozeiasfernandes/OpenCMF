# core/workspace/__init__.py
from .workspace_manager import WorkspaceManager
from .registry import WorkspaceRegistry
from .state import WorkspaceState
from .contracts import IModule, IWorkspaceTab

__all__ = ["WorkspaceManager", "WorkspaceRegistry", "WorkspaceState", "IModule", "IWorkspaceTab"]