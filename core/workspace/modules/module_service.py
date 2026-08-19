from __future__ import annotations

import logging
from pathlib import Path
import importlib.util
from typing import Optional

from core.settings.paths.list_paths import MODULES_DIR

class ModuleService:
    """Serviço responsável pelo gerenciamento, resolução e carregamento dinâmico dos módulos da aplicação de forma automatizada."""

    def __init__(self, modules_dir: str | Path | None = None):
        # Utiliza o diretório padrão de módulos
        self.modules_dir = Path(modules_dir) if modules_dir is not None else Path(MODULES_DIR)

    def _resolve_module_path(self, id_modulo: str) -> Optional[tuple[str, Path]]:
        """Varre o diretório dinamicamente para encontrar a pasta correspondente ao ID do módulo."""
        clean_id = id_modulo.lower().strip()
        if clean_id.endswith("_module"):
            clean_name = clean_id[:-7]
        else:
            clean_name = clean_id

        # Procura diretamente na pasta correspondente
        module_folder = self.modules_dir / clean_name
        module_file = module_folder / f"{clean_name}_module.py"

        if module_file.is_file():
            return clean_name, module_file

        # Fallback de busca dinâmica caso o ID venha em formato diferente (varre as pastas existentes)
        if self.modules_dir.is_dir():
            for child in self.modules_dir.iterdir():
                if child.is_dir():
                    folder_name = child.name.lower()
                    if folder_name == clean_name or f"{folder_name}_module" == clean_id:
                        candidate_file = child / f"{folder_name}_module.py"
                        if candidate_file.is_file():
                            return folder_name, candidate_file

        return None

    def get_module_class(self, id_modulo: str) -> Optional[type]:
        """Busca e retorna dinamicamente a classe 'Module' associada ao identificador informado, varrendo o diretório."""
        try:
            resolved = self._resolve_module_path(id_modulo)
            if not resolved:
                logging.warning(f"Módulo '{id_modulo}' não encontrado no diretório de módulos.")
                return None

            clean_name, module_file_path = resolved

            # Monta o caminho do pacote Python para importação dinâmica
            module_package_str = f"{self.modules_dir.name}.{clean_name}.{clean_name}_module"

            spec = importlib.util.spec_from_file_location(module_package_str, module_file_path)
            if not spec or not spec.loader:
                return None

            module_obj = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module_obj)

            return getattr(module_obj, "Module", None)

        except Exception as e:
            logging.error(f"Erro ao carregar dinamicamente o módulo '{id_modulo}': {e}", exc_info=True)
            return None


if __name__ == "__main__":
    # Configuração básica de logs para o teste isolado
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    print("--- Testando o ModuleService ---")
    service = ModuleService()

    # Testando com o ID abreviado "test" que agora mapeia para "test_module"
    modulo_teste = "test"
    print(f"Buscando classe para: '{modulo_teste}' em {service.modules_dir}...")

    cls = service.get_module_class(modulo_teste)

    if cls:
        print(f"Sucesso! Classe encontrada: {cls}")
    else:
        print(f"Falha: O módulo '{modulo_teste}' não pôde ser resolvido ou não possui a classe 'Module'.")