# core/workspace/__init__.py
from .workspace_manager import WorkspaceManager
from models.registry import WorkspaceRegistry
from patient.state import WorkspaceState
from models.contracts import IModule, IWorkspaceTab

__all__ = ["WorkspaceManager", "WorkspaceRegistry", "WorkspaceState", "IModule", "IWorkspaceTab"]

