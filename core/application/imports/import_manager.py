from pathlib import Path
from typing import Any, List, Union
from core.application.imports.importers.importer_registry import ImporterRegistry

class ImportManager:
    """Orquestrador principal do subsistema de importações."""

    def __init__(self, registry: ImporterRegistry):
        self.registry = registry

    def import_source(self, source: Union[Path, List[Path]], options: Any = None) -> Any:
        """
        Processa a importação de uma fonte (arquivo ou lista de arquivos/diretórios),
        encontrando o importador adequado, carregando os dados e criando o objeto final.
        """
        # Localiza o importador instanciado correto através do Registry
        importer = self.registry.get_importer(source)

        # Lê os dados brutos utilizando o importador específico
        raw_data = importer.load(source, options)

        # Empacota no formato padrão consumido pelo Scene Manager
        scene_object = importer.create_object(raw_data)

        return scene_object