import importlib.util
import os
from core.base import ModuloBase


class ModuloFactory:
    @staticmethod
    def carregar_modulo(id_modulo: str) -> ModuloBase:
        # Importa dinamicamente um módulo da pasta /modulos
        try:
            nome_modulo = f"modulos.{id_modulo}"

            # Verifica se o arquivo existe no caminho especificado
            spec = importlib.util.find_spec(nome_modulo)
            if spec is None:
                print(f"Erro: {id_modulo}.py não encontrado em /modulos")
                return None

            # Carrega o arquivo .py na memória
            modulo_python = importlib.import_module(nome_modulo)

            # Instancia a classe 'Modulo' que deve existir dentro de cada arquivo
            if hasattr(modulo_python, "Modulo"):
                return modulo_python.Modulo()

            print(f"Erro: {id_modulo}.py não contém a classe 'Modulo'")
            return None

        except Exception as e:
            # Captura falhas de importação ou erros internos do módulo
            print(f"Falha ao carregar {id_modulo}: {e}")
            return None