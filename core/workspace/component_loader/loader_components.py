import importlib.util
import logging
import traceback
import inspect
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("ComponentLoader")


class ComponentLoader:
    @staticmethod
    def carregar(caminho: Path, context: Any, categoria: Optional[str] = None) -> Optional[Any]:
        if not caminho.exists():
            logger.error(f"Arquivo não encontrado: {caminho}")
            return None

        try:
            spec = importlib.util.spec_from_file_location(caminho.stem, caminho)
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            instancia = ComponentLoader._instanciar_dinamico(module, context)

            if instancia:
                instancia.__module_path__ = caminho
                return instancia

            logger.warning(f"O módulo {caminho.name} não pôde ser instanciado.")
            return None

        except Exception:
            logger.error(f"Falha ao carregar {caminho.name}:\n{traceback.format_exc()}")
            return None

    @staticmethod
    def _instanciar_dinamico(module: Any, context: Any) -> Optional[Any]:
        factory = getattr(module, "create_component", None)
        if callable(factory):
            return factory(context)

        component_cls = getattr(module, "Component", None)
        if component_cls and inspect.isclass(component_cls):
            return ComponentLoader._injetar_dependencias(component_cls, context)

        return None

    @staticmethod
    def _injetar_dependencias(cls: Any, context: Any) -> Any:
        deps = {
            "modulo": context,
            "tool_manager": getattr(context, "tool_manager", None),
            "scene_manager": getattr(context, "scene_manager", None)
        }

        sig = inspect.signature(cls.__init__)
        params = {k: v for k, v in deps.items() if k in sig.parameters}

        try:
            return cls(**params)
        except Exception:
            return cls()