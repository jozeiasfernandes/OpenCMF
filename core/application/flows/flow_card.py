from __future__ import annotations

from typing import Any, Dict
from PySide6 import QtCore, QtWidgets, QtGui

# Localization
from core.settings.localization.translator import tr


class FlowsCard(QtWidgets.QFrame):
    """Card interativo que exibe um fluxo de trabalho composto por um título e uma sequência de módulos."""

    clicked = QtCore.Signal(str)

    def __init__(self, data: Dict[str, Any], flow_path: str, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.data = data
        self.flow_path = flow_path

        self._setup_ui()

    # =========================================================================
    # UI SETUP & LAYOUT
    # =========================================================================
    def _setup_ui(self) -> None:
        """Configura as propriedades visuais principais e constrói o layout do card."""
        self.setObjectName("FlowsCard")
        self.setCursor(QtCore.Qt.PointingHandCursor)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        # 1. Bloco de Destaque (Título Principal do Fluxo)
        flow_name = self.data.get("name", "Unnamed")
        self.title_block = self._create_flow_block(flow_name)
        layout.addWidget(self.title_block)

        # 2. Sequência de Módulos Associados
        self._populate_module_sequence(layout)

        layout.addStretch()

    def _populate_module_sequence(self, layout: QtWidgets.QHBoxLayout) -> None:
        """Itera sobre a sequência de módulos, adicionando separadores e widgets correspondentes."""
        modules = self.data.get("sequence", [])

        for index, technical_name in enumerate(modules):
            if index > 0:
                layout.addWidget(self._create_arrow_separator())

            friendly_name = self._format_module_name(technical_name)
            module_widget = self._create_module_block(friendly_name)
            layout.addWidget(module_widget)

    def _create_flow_block(self, text: str) -> QtWidgets.QFrame:
        """Cria o bloco principal estruturado para o título do fluxo."""
        block = QtWidgets.QFrame()
        block.setObjectName("FluxoCardMainBlock")
        block.setFixedSize(200, 80)

        layout = QtWidgets.QVBoxLayout(block)

        label = QtWidgets.QLabel(text)
        label.setObjectName("FluxoCardTitleLabel")
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(label)
        return block

    def _create_module_block(self, text: str) -> QtWidgets.QLabel:
        """Cria o bloco visual correspondente a um módulo individual da sequência."""
        label = QtWidgets.QLabel(text)
        label.setObjectName("FluxoCardModuleLabel")
        label.setFixedSize(140, 70)
        label.setAlignment(QtCore.Qt.AlignCenter)
        return label

    def _create_arrow_separator(self) -> QtWidgets.QLabel:
        """Cria o elemento visual de seta para indicar a ordem da sequência."""
        arrow = QtWidgets.QLabel("➔")
        arrow.setObjectName("FluxoCardArrow")
        return arrow

    # =========================================================================
    # HELPERS & BUSINESS LOGIC
    # =========================================================================
    def _format_module_name(self, technical_name: str) -> str:
        """Traduz dinamicamente o nome do módulo usando o sistema de tradução, com fallback algorítmico."""
        clean_name = technical_name[:-7] if technical_name.endswith("_module") else technical_name
        clean_name = clean_name.lower().strip()

        translation_key = f"modules.{clean_name}"
        translated = tr(translation_key)

        # Se não encontrar tradução no arquivo de idiomas, aplica o fallback formatado
        if translated == translation_key:
            return clean_name.replace("_", " ").capitalize()

        return translated

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================
    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.flow_path)
        super().mousePressEvent(event)


