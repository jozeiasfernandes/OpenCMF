from __future__ import annotations

import logging
from typing import Optional, Any
from PySide6 import QtWidgets, QtCore
from core.components.bases.base_sidepanel import BaseSidePanel

logger = logging.getLogger("ComponentsLogPanel")


class Component(BaseSidePanel):
    """
    Painel lateral para exibição de logs e eventos dos componentes e do sistema.
    Herda de BaseSidePanel para integração com a arquitetura baseada em composição.
    """
    side_panel_name = "Log de Componentes"

    def __init__(self, context: Any, title: str = "Log de Componentes", parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(context=context, title=title, parent=parent)
        self.setup_component()

    def setup_ui(self) -> None:
        """Configura a interface do usuário para exibição dos logs."""
        self.layout.setSpacing(8)

        # ── Área de Texto / Log ──────────────────────────────────────────────
        self.text_log = QtWidgets.QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setStyleSheet(
            "background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas, monospace; font-size: 10pt;"
        )
        self.layout.addWidget(self.text_log)

        # ── Controles Inferiores (Botões de Ação) ────────────────────────────
        layout_botoes = QtWidgets.QHBoxLayout()
        layout_botoes.setContentsMargins(0, 0, 0, 0)

        self.btn_limpar = QtWidgets.QPushButton("Limpar Logs")
        self.btn_limpar.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_limpar.clicked.connect(self.limpar_logs)
        layout_botoes.addWidget(self.btn_limpar)

        self.layout.addLayout(layout_botoes)

        # Adiciona uma mensagem inicial de boas-vindas/sistema
        self.adicionar_log("Painel de logs de componentes inicializado com sucesso.")

    def adicionar_log(self, mensagem: str) -> None:
        """Adiciona uma nova linha de log ao painel."""
        if hasattr(self, "text_log") and self.text_log:
            self.text_log.append(mensagem)
            # Rola para o final automaticamente
            scrollbar = self.text_log.verticalScrollBar()
            if scrollbar:
                scrollbar.setValue(scrollbar.maximum())

    def limpar_logs(self) -> None:
        """Limpa todo o conteúdo da área de logs."""
        if hasattr(self, "text_log") and self.text_log:
            self.text_log.clear()

    def dispose(self) -> None:
        """Limpeza de recursos do painel."""
        super().dispose()


if __name__ == "__main__":
    import sys
    from core.components.bases.base_toolbar import AppContext
    from core.components.bases.base_tool.tool_manager import ToolManager
    from core.scene.scene_manager import SceneManager
    from core.scene.scene_state import SceneState
    from core.scene.events.event_bus import EventBus

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # Configuração de contexto simulado para testes
    event_bus = EventBus()
    scene_manager = SceneManager(
        state=SceneState(),
        event_bus=event_bus,
        object_registry=None,
        actor_registry=None,
        selection_manager=None
    )

    app_context = AppContext(
        scene_manager=scene_manager,
        tool_manager=ToolManager(),
        event_bus=event_bus
    )

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Teste - ComponentsLogPanel")
    window.resize(600, 400)

    log_panel = Component(context=app_context, title="Log de Componentes")
    window.setCentralWidget(log_panel)

    # Simula a adição de logs
    log_panel.adicionar_log("[INFO] Sistema iniciado.")
    log_panel.adicionar_log("[DEBUG] Carregando módulos de componentes...")

    window.show()
    sys.exit(app.exec())