from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Tool:
    """Representa uma ferramenta individual."""
    path: Path
    name: str

    def __repr__(self):
        return self.name


@dataclass(frozen=True)
class Toolbar:
    """Representa uma coleção de ferramentas."""
    path: Path
    display_name: str

    def __repr__(self):
        return self.display_name