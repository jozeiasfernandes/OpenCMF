from pathlib import Path
from typing import List, Type, Union
from core.imports.importers.base_importer import BaseImporter


class ImporterRegistry:
    """Registro central de importadores do OpenCMF."""

    def __init__(self):
        self._importers: List[Type[BaseImporter]] = []

    def register(self, importer_class: Type[BaseImporter]):
        """Registra uma nova classe de importador no sistema."""
        if importer_class not in self._importers:
            self._importers.append(importer_class)

    def get_importer(self, source: Union[Path, List[Path]]) -> BaseImporter:
        """
        Encontra o importador adequado utilizando triagem rápida (`supports`)
        seguida de validação profunda (`validate`).
        """
        primary_path = source[0] if isinstance(source, list) else source

        for importer_class in self._importers:
            # Triagem rápida de classe (evita instanciar desnecessariamente)
            if importer_class.supports(primary_path) or isinstance(source, list):
                if importer_class.validate(source):
                    # Retorna uma instância do importador válido
                    return importer_class()

        raise ValueError(f"Nenhum importador compatível foi encontrado para a origem: {source}")