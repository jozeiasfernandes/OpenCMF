import importlib.util
import logging
from pathlib import Path

logger = logging.getLogger("ComponentLoader")


class ComponentLoader:
    @staticmethod
    def carregar(caminho: Path, modulo_instancia):
        if not caminho.exists():
            logger.error(f"Arquivo não encontrado: {caminho}")
            return None

        try:
            spec = importlib.util.spec_from_file_location(caminho.stem, caminho)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "Component"):
                instancia = module.Component(modulo=modulo_instancia)
                instancia.__module_path__ = caminho
                logger.debug(f"Instância de 'Component' criada para {caminho.stem}")
                return instancia

            logger.warning(f"O arquivo {caminho.name} não possui a classe 'Component'.")
            return None

        except Exception as e:
            logger.error(f"Falha na execução do módulo {caminho.name}: {e}")
            logger.error(logging.traceback.format_exc())
            return None