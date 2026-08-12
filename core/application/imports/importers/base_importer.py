from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar, List, Union

class BaseImporter(ABC):
    """Classe base para todos os importadores do OpenCMF."""

    name: ClassVar[str] = ""
    supported_extensions: ClassVar[tuple[str, ...]] = ()
    supports_multiple_files: ClassVar[bool] = False

    @classmethod
    def supports(cls, source: Path) -> bool:
        """
        Verifica rapidamente se este importador é candidato com base na extensão
        ou se a subclasse permite diretórios (ex: pastas DICOM).
        """
        if source.is_dir():
            return False
        return source.suffix.lower() in cls.supported_extensions

    @classmethod
    @abstractmethod
    def validate(cls, source: Union[Path, List[Path]]) -> bool:
        """
        Validação profunda (integridade do arquivo, cabeçalhos, etc.).
        Pode ser executada sem instanciar a classe.
        """
        pass

    @abstractmethod
    def load(self, source: Union[Path, List[Path]], options: Any = None) -> Any:
        """Lê os dados brutos da origem."""
        pass

    @abstractmethod
    def create_object(self, data: Any) -> Any:
        """Cria e retorna o objeto interno do OpenCMF a partir dos dados lidos."""
        pass