import importlib.util
from core.base_module.base import ModuloBase


class ModuloFactory:
    @staticmethod
    def carregar_modulo(id_modulo: str) -> ModuloBase:
        try:
            nome_modulo = f"modules.{id_modulo}"

            spec = importlib.util.find_spec(nome_modulo)
            if spec is None:
                print(f"Error: {id_modulo}.py not found in /modules")
                return None

            module_obj = importlib.import_module(nome_modulo)

            if hasattr(module_obj, "Modulo"):
                return module_obj.Modulo()

            print(f"Error: {id_modulo}.py does not contain 'Modulo' class")
            return None

        except Exception as e:
            print(f"Failed to load module {id_modulo}: {e}")
            return None