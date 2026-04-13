import json
from pathlib import Path
from typing import Tuple, Optional, Dict
from PySide6 import QtWidgets, QtCore
from core.base import ModuloBase


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Visualizador de Tomografia"
        self.id = "modulo.tomografia"
        self.caminho_dicom: Optional[str] = None
        self._is_initialized = False

        # Referências de UI para atualização dinâmica
        self.lbl_caminho = None

    def inicializar(self, caminho_paciente: str) -> None:
        """Inicia o módulo e sincroniza os dados do paciente."""
        super().inicializar(caminho_paciente)
        self._is_initialized = True
        # Pequeno delay para garantir que a UI lateral foi montada antes de atualizar
        QtCore.QTimer.singleShot(150, self._atualizar_ui_requisitos)

    def verificar_pre_requisitos(self) -> Tuple[bool, str]:
        if not self.pasta_paciente:
            return False, "Nenhum paciente selecionado."

        path_info = Path(self.pasta_paciente) / "projeto" / "info.json"
        if not path_info.exists():
            return False, "Arquivo info.json não encontrado."

        try:
            with open(path_info, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.caminho_dicom = dados.get("caminhos", {}).get("dicom")

            if not self.caminho_dicom:
                return False, "Caminho da Tomografia não configurado."

            diretorio_dicom = Path(self.caminho_dicom)
            if not diretorio_dicom.exists():
                return False, "Pasta DICOM não encontrada."

            arquivos_dicom = list(diretorio_dicom.glob("*.dcm"))
            if len(arquivos_dicom) > 0:
                return True, ""

            return False, "A pasta DICOM está vazia."
        except Exception as e:
            return False, f"Erro na validação: {str(e)}"

    def get_workspace(self) -> QtWidgets.QWidget:
        """Retorna a área central (MPR)."""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        view_area = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(view_area)
        grid.setSpacing(2)
        grid.setContentsMargins(1, 1, 1, 1)

        planos = ["Axial", "Sagital", "Coronal", "3D"]
        for i, nome in enumerate(planos):
            quadrante = QtWidgets.QFrame()
            quadrante.setStyleSheet("background-color: black; border: 1px solid #222;")
            q_lay = QtWidgets.QVBoxLayout(quadrante)
            lbl = QtWidgets.QLabel(nome)
            lbl.setStyleSheet("color: #777; font-weight: bold; font-size: 10px;")
            q_lay.addWidget(lbl, alignment=QtCore.Qt.AlignTop)
            grid.addWidget(quadrante, i // 2, i % 2)

        layout.addWidget(view_area, stretch=1)
        return container

    def get_workspace_toolbar(self) -> QtWidgets.QToolBar:
        toolbar = QtWidgets.QToolBar("Ferramentas DICOM")
        toolbar.addAction("Sincronizar Vistas")
        toolbar.addSeparator()
        toolbar.addAction("Resetar Contraste")
        return toolbar

    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        """
        Define as abas verticais (East) que o WorkspaceManager irá criar.
        """
        # --- ABA ABRIR ---
        aba_abrir = QtWidgets.QWidget()
        lay_abrir = QtWidgets.QVBoxLayout(aba_abrir)

        lay_abrir.addWidget(QtWidgets.QLabel("<b>GESTÃO DE ARQUIVOS</b>"))

        self.lbl_caminho = QtWidgets.QLabel("Pasta Atual:\nVerificando...")
        self.lbl_caminho.setWordWrap(True)
        self.lbl_caminho.setStyleSheet("color: #aaa; font-size: 10px; margin: 5px 0;")
        lay_abrir.addWidget(self.lbl_caminho)

        btn_recarregar = QtWidgets.QPushButton("📁 Recarregar Pasta")
        btn_recarregar.setMinimumHeight(35)
        btn_recarregar.clicked.connect(self._atualizar_ui_requisitos)
        lay_abrir.addWidget(btn_recarregar)

        lay_abrir.addStretch()

        # Botão de finalizar fixado no rodapé desta aba
        btn_concluir = QtWidgets.QPushButton("Finalizar Etapa")
        btn_concluir.setStyleSheet("font-weight: bold; padding: 8px; background-color: #27ae60; color: white;")
        btn_concluir.clicked.connect(self._on_conclude_clicked)
        lay_abrir.addWidget(btn_concluir)

        # --- ABA FILTRAR ---
        aba_filtrar = QtWidgets.QWidget()
        lay_filtrar = QtWidgets.QVBoxLayout(aba_filtrar)

        lay_filtrar.addWidget(QtWidgets.QLabel("<b>FILTROS DICOM</b>"))
        lay_filtrar.addSpacing(10)
        lay_filtrar.addWidget(QtWidgets.QLabel("Threshold (HU):"))

        self.slider_hu = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_hu.setRange(-1000, 3000)
        self.slider_hu.setValue(200)
        lay_filtrar.addWidget(self.slider_hu)

        lbl_hint = QtWidgets.QLabel("Osso: +200 a +1000\nAr: -1000")
        lbl_hint.setStyleSheet("color: #666; font-size: 9px;")
        lay_filtrar.addWidget(lbl_hint)

        lay_filtrar.addStretch()

        # Retorna o dicionário com os nomes que aparecerão nas abas laterais
        return {
            "Abrir": aba_abrir,
            "Filtrar": aba_filtrar
        }

    def _atualizar_ui_requisitos(self):
        """Atualiza o texto do caminho DICOM na interface lateral."""
        sucesso, msg = self.verificar_pre_requisitos()
        if self.lbl_caminho:
            if self.caminho_dicom:
                folder_name = Path(self.caminho_dicom).name
                self.lbl_caminho.setText(f"Pasta Atual:\n{folder_name}")
            else:
                self.lbl_caminho.setText(f"Pasta Atual:\n{msg}")

    def validar_passagem(self) -> bool:
        return self._is_initialized

    def _on_conclude_clicked(self) -> None:
        if self.validar_passagem():
            self.concluido.emit()
        else:
            QtWidgets.QMessageBox.warning(None, "Aviso", "Módulo não inicializado corretamente.")