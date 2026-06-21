from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Tool:
    """Representa uma ferramenta individual."""
    path: Path
    name: str

    def __repr__(self):
        return self.name


@dataclass
class Toolbar:
    """Representa uma coleção de ferramentas."""
    path: Path
    display_name: str

    def __repr__(self):
        return self.display_name