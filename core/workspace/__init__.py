# core/workspace/__init__.py
from core.workspace.workspace_manager import WorkspaceManager
from core.workspace.models.registry import WorkspaceRegistry
from core.workspace.patient.state import WorkspaceState
from core.workspace.models.contracts import IModule, IWorkspaceTab

__all__ = ["WorkspaceManager", "WorkspaceRegistry", "WorkspaceState", "IModule", "IWorkspaceTab"]

