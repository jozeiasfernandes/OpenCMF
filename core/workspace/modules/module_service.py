from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import Optional

from core.settings.paths.list_paths import MODULES_DIR


class ModuleService:
    """Serviço responsável pelo gerenciamento, resolução e carregamento dinâmico dos módulos da aplicação de forma automatizada."""

    def __init__(self, modules_dir: str | Path | None = None):
        # Utiliza o MODULES_DIR importado por padrão, permitindo override opcional se necessário
        self.modules_dir = Path(modules_dir) if modules_dir is not None else Path(MODULES_DIR)

        # Mapeamento para casos legados, apelidos especiais ou abreviações
        self._mapeamento = {
            "Pacient": "new_project",
            "modulo.pacient": "new_project",
            "test": "test_module"
        }

    def get_module_class(self, id_modulo: str) -> Optional[type]:
        """Busca e retorna dinamicamente a classe 'Module' associada ao identificador informado, lendo o diretório."""
        try:
            # 1. Resolve o nome base do módulo (considerando apelidos ou convertendo para minúsculo)
            target = self._mapeamento.get(id_modulo, id_modulo.lower())

            # Remove o sufixo '_module' se já vier no id_modulo para evitar duplicação (ex: 'teste_module' -> 'teste')
            if target.endswith("_module"):
                clean_name = target[:-7]
            else:
                clean_name = target

            # 2. Conforme sua regra: MODULES_DIR / module / (module + "_module.py")
            module_folder_name = clean_name
            module_file_name = f"{clean_name}_module.py"

            module_file_path = self.modules_dir / module_folder_name / module_file_name

            if not module_file_path.is_file():
                logging.warning(f"Arquivo do módulo não encontrado no caminho esperado: {module_file_path}")
                return None

            # 3. Monta o caminho do pacote Python para importação dinâmica
            module_package_str = f"{self.modules_dir.name}.{module_folder_name}.{clean_name}_module"

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