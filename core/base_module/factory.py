import importlib.util
import sys
from pathlib import Path
from core.base_module.base import ModuloBase


class ModuloFactory:
    @staticmethod
    def carregar_modulo(id_modulo: str) -> ModuloBase:
        try:
            root = str(Path(__file__).parent.parent.parent)
            if root not in sys.path:
                sys.path.insert(0, root)

            mapeamento = {
                "Paciente": "patients",
                "modulo.paciente": "patients"
            }

            nome_arquivo = mapeamento.get(id_modulo, id_modulo.lower())
            nome_modulo = f"modules.{nome_arquivo}"

            spec = importlib.util.find_spec(nome_modulo)
            if not spec:
                return None

            module_obj = importlib.import_module(nome_modulo)
            classe_modulo = getattr(module_obj, "Modulo", None)

            return classe_modulo() if classe_modulo else None

        except Exception:
            return None