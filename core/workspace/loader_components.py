import importlib.util
import logging
import traceback
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("ComponentLoader")


class ComponentLoader:
    @staticmethod
    def carregar(
        caminho: Path,
        modulo_instancia: Any,
        categoria: Optional[str] = None,
    ):
        if not caminho.exists():
            logger.error(f"Arquivo não encontrado: {caminho}")
            return None

        try:
            spec = importlib.util.spec_from_file_location(caminho.stem, caminho)
            if spec is None or spec.loader is None:
                logger.error(f"Spec inválido para {caminho}")
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if categoria == "central_area":
                instancia = ComponentLoader._instanciar_central(
                    module, caminho, modulo_instancia
                )
                if instancia is not None:
                    instancia.__module_path__ = caminho
                return instancia

            if hasattr(module, "Component"):
                instancia = module.Component(modulo=modulo_instancia)
                instancia.__module_path__ = caminho
                logger.debug(f"Instância de 'Component' criada para {caminho.stem}")
                return instancia

            logger.warning(f"O arquivo {caminho.name} não possui a classe 'Component'.")
            return None

        except Exception as e:
            logger.error(f"Falha na execução do módulo {caminho.name}: {e}")
            logger.error(traceback.format_exc())
            return None

    @staticmethod
    def _instanciar_central(module, caminho: Path, modulo_instancia: Any):
        if hasattr(module, "Component"):
            try:
                return module.Component(modulo=modulo_instancia)
            except TypeError:
                return module.Component()

        sm = getattr(modulo_instancia, "scene_manager", None)
        stem = caminho.stem

        if stem == "window_registration":
            cls = getattr(module, "WindowRegistration", None)
            if cls:
                return cls(scene_manager=sm)
        elif stem == "windows_3d":
            cls = getattr(module, "Janela3DSurface", None)
            if cls:
                return cls("Superfície 3D", "#2C3E50", None, sm)
        elif stem == "window_2d":
            cls = getattr(module, "Janela2D", None)
            if cls:
                return cls("2D", "#3498DB", None)
        elif stem == "window_3d_dicom":
            cls = getattr(module, "Janela3D", None)
            if cls:
                return cls("3D DICOM", "#E74C3C", None)

        logger.warning(
            "Área central sem Component nem mapeamento conhecido: %s",
            caminho.name,
        )
        return None