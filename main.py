import sys
import json
import logging
from pathlib import Path
from functools import partial
from typing import Optional

from PySide6 import QtWidgets, QtCore
from core.base import FluxoBase
from core.factory import ModuloFactory

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class MainWindow(QtWidgets.QMainWindow):
    WINDOW_TITLE = "OpenCMF - Modular Surgical Planning"
    DEFAULT_GEOMETRY = (150, 50, 1024, 650)
    TOOLBOX_MIN_WIDTH = 32
    TOOLBOX_MAX_WIDTH = 350

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._init_ui()
        self.carregar_fluxo_inicial(Path("fluxos/ortog.json"))

    def _setup_window(self) -> None:
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setGeometry(*self.DEFAULT_GEOMETRY)

    def _init_ui(self) -> None:
        self.tabs_modulos = QtWidgets.QTabWidget()
        self.tabs_modulos.setDocumentMode(True)
        self.setCentralWidget(self.tabs_modulos)

    def carregar_fluxo_inicial(self, caminho_json: Path) -> None:
        if not caminho_json.exists():
            logging.error(f"Arquivo não encontrado: {caminho_json}")
            return

        try:
            with caminho_json.open('r', encoding="utf-8") as f:
                dados = json.load(f)

            self.fluxo = FluxoBase(dados)

            for id_mod in self.fluxo.sequencia:
                modulo = ModuloFactory.carregar_modulo(id_mod)
                if modulo:
                    self._adicionar_modulo_aba(id_mod, modulo)
        except Exception as e:
            logging.exception(f"Erro ao carregar fluxo: {e}")

    def _adicionar_modulo_aba(self, id_mod: str, modulo) -> None:
        aba_modulo = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(aba_modulo)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(modulo.get_workspace(), stretch=1)
        toolbox = self._criar_toolbox_lateral(modulo.get_toolbox())
        layout.addWidget(toolbox)

        # Formata o ID para título da aba
        titulo = id_mod.split('_')[-1].capitalize()
        self.tabs_modulos.addTab(aba_modulo, titulo)

    def _criar_toolbox_lateral(self, widget_ferramentas: QtWidgets.QWidget) -> QtWidgets.QTabWidget:
        toolbox = QtWidgets.QTabWidget()
        toolbox.setTabPosition(QtWidgets.QTabWidget.East)
        toolbox.setFixedWidth(self.TOOLBOX_MIN_WIDTH)

        widget_ferramentas.setVisible(False)
        toolbox.addTab(widget_ferramentas, "Ferramentas")
        toolbox.tabBarClicked.connect(partial(self._on_toolbox_clicked, toolbox))

        return toolbox

    def _on_toolbox_clicked(self, toolbox: QtWidgets.QTabWidget, index: int) -> None:
        conteudo = toolbox.widget(index)

        # Toggle se clicar na aba ativa, caso contrário, expande
        if toolbox.currentIndex() == index:
            nova_visibilidade = not conteudo.isVisible()
            self._set_toolbox_state(toolbox, conteudo, expandido=nova_visibilidade)
        else:
            self._set_toolbox_state(toolbox, conteudo, expandido=True)

    def _set_toolbox_state(self, toolbox: QtWidgets.QTabWidget, conteudo: QtWidgets.QWidget, expandido: bool) -> None:
        conteudo.setVisible(expandido)
        largura = self.TOOLBOX_MAX_WIDTH if expandido else self.TOOLBOX_MIN_WIDTH
        toolbox.setFixedWidth(largura)


def aplicar_estilo_qss(app: QtWidgets.QApplication, caminho_qss: Path) -> None:
    try:
        if caminho_qss.exists():
            with caminho_qss.open("r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
    except Exception as e:
        logging.error(f"Erro de estilo: {e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    aplicar_estilo_qss(app, Path("temas/escuro.qss"))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())