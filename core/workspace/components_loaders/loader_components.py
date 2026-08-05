import importlib.util
import logging
import traceback
import inspect
import sys
import hashlib
from pathlib import Path
from typing import Any, Optional
from core.components.bases.base_component import BaseComponent

logger = logging.getLogger("ComponentLoader")


class ComponentLoader:
    @staticmethod
    def carregar(caminho: Path, context: Any) -> Optional[Any]:
        if not caminho.exists():
            logger.error(f"Arquivo não encontrado: {caminho}")
            return None

        try:
            # 1. Carregar módulo com nome determinístico via MD5
            path_hash = hashlib.md5(str(caminho).encode("utf-8")).hexdigest()[:8]
            module_name = f"dynamic_component_{caminho.stem}_{path_hash}"
            spec = importlib.util.spec_from_file_location(module_name, caminho)

            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)

            # Registra no sys.modules para evitar problemas de escopo e isinstance
            sys.modules[module_name] = module

            spec.loader.exec_module(module)

            # 2. Tentar instanciar
            instancia = ComponentLoader._instanciar_dinamico(module, context)

            if instancia:
                # 3. Ciclo de vida: Chamar o contrato obrigatório
                if hasattr(instancia, "setup_component"):
                    instancia.setup_component()
                return instancia

            return None
        except Exception:
            logger.error(f"Falha ao carregar {caminho.name}:\n{traceback.format_exc()}")
            return None

    @staticmethod
    def _instanciar_dinamico(module: Any, context: Any) -> Optional[Any]:
        factory = getattr(module, "create_component", None)
        if callable(factory):
            return factory(context)

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseComponent) and obj is not BaseComponent:
                return ComponentLoader._injetar_dependencias(obj, context)

        return None

    @staticmethod
    def _injetar_dependencias(cls: Any, context: Any) -> Any:
        try:
            sig = inspect.signature(cls.__init__)
            if "context" in sig.parameters:
                return cls(context=context)
        except (TypeError, ValueError):
            pass

        # Fallback caso ocorra algum problema na inspeção ou não utilize o parâmetro explicitamente
        try:
            return cls(context=context)
        except TypeError:
            return cls()