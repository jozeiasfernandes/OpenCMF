# core/components/__init__.py

from .registry import ComponentRegistry, ComponentType
from .scanner import ComponentScanner
from .bases.base_component import BaseComponent

# Facilita a importação de toda a infraestrutura
__all__ = ["ComponentRegistry", "ComponentType", "ComponentScanner", "BaseComponent"]