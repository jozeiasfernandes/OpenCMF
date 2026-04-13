# /modulos/Tomografia.py

import json
from pathlib import Path
from typing import Tuple, Optional
from PySide6 import QtWidgets, QtCore
from core.base import ModuloBase


class Modulo(ModuloBase):  # Renomeado de ModuloTomografia para Modulo (padrão Factory)
    def __init__(self):
        super().__init__()
        self.nome = "Visualizador de Tomografia"
        self.id = "modulo.tomografia"
        self.caminho_dicom: Optional[str] = None
        self._is_initialized = False

    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)
        self._is_initialized = True

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
                print(">>> [ERRO] Caminho DICOM não definido no info.json")
                return False, "Caminho da Tomografia não configurado."

            diretorio_dicom = Path(self.caminho_dicom)
            if not diretorio_dicom.exists():
                print(f">>> [ERRO] Diretório não encontrado: {diretorio_dicom}")
                return False, "Pasta de tomografia não existe no disco."

            # Varredura de arquivos para log no terminal
            arquivos_dicom = list(diretorio_dicom.glob("*.dcm"))
            qtd = len(arquivos_dicom)

            if qtd > 0:
                print(f">>> [SUCESSO] Módulo Tomografia: {qtd} arquivos .dcm encontrados.")
                return True, ""

            print(f">>> [AVISO] Pasta encontrada mas sem arquivos .dcm em: {diretorio_dicom}")
            return False, "A pasta selecionada não contém arquivos DICOM (.dcm)."

        except Exception as e:
            print(f">>> [CRÍTICO] Falha ao ler requisitos da Tomografia: {e}")
            return False, f"Erro ao validar requisitos: {str(e)}"

    def get_workspace(self) -> QtWidgets.QWidget:
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Barra superior (Toolbar)
        layout.addWidget(self.get_workspace_toolbar())

        # Área de Visualização Multi-Planar (MPR)
        view_area = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(view_area)
        grid.setSpacing(2)
        grid.setContentsMargins(1, 1, 1, 1)

        planos = ["Axial", "Sagital", "Coronal", "3D"]
        for i, nome in enumerate(planos):
            quadrante = self._criar_quadrante(nome)
            grid.addWidget(quadrante, i // 2, i % 2)

        layout.addWidget(view_area, stretch=1)
        return container

    def _criar_quadrante(self, titulo: str) -> QtWidgets.QFrame:
        frame = QtWidgets.QFrame()
        frame.setStyleSheet("background-color: black; border: 1px solid #222;")
        flay = QtWidgets.QVBoxLayout(frame)

        lbl = QtWidgets.QLabel(titulo)
        lbl.setStyleSheet("color: #555; font-weight: bold; font-size: 10px;")
        lbl.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        flay.addWidget(lbl)
        flay.addStretch()
        return frame

    def get_workspace_toolbar(self) -> QtWidgets.QToolBar:
        toolbar = QtWidgets.QToolBar("Ferramentas DICOM")
        toolbar.setIconSize(QtCore.QSize(24, 24))
        toolbar.addAction("Sincronizar Vistas")
        toolbar.addSeparator()
        toolbar.addAction("Resetar Contraste")
        return toolbar

    def get_toolbox(self) -> QtWidgets.QWidget:
        # Criamos o widget principal da toolbox
        toolbox_principal = QtWidgets.QWidget()
        layout_principal = QtWidgets.QVBoxLayout(toolbox_principal)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        # Criamos o componente de Abas
        self.tabs = QtWidgets.QTabWidget()

        # --- ABA 1: ABRIR DICOM ---
        aba_abrir = QtWidgets.QWidget()
        lay_abrir = QtWidgets.QVBoxLayout(aba_abrir)

        lay_abrir.addWidget(QtWidgets.QLabel("<b>GESTÃO DE ARQUIVOS</b>"))

        # Exibe o caminho atual vindo do ModuloPaciente
        folder_name = Path(self.caminho_dicom).name if self.caminho_dicom else "Não definido"
        lbl_caminho = QtWidgets.QLabel(f"Pasta Atual:\n{folder_name}")
        lbl_caminho.setWordWrap(True)
        lbl_caminho.setStyleSheet("color: #aaa; font-size: 10px; margin-bottom: 10px;")
        lay_abrir.addWidget(lbl_caminho)

        btn_recarregar = QtWidgets.QPushButton("📁 Recarregar Pasta")
        btn_recarregar.setMinimumHeight(40)
        btn_recarregar.clicked.connect(self.verificar_pre_requisitos)
        lay_abrir.addWidget(btn_recarregar)

        lay_abrir.addStretch()
        self.tabs.addTab(aba_abrir, "📂 Abrir")

        # --- ABA 2: FILTRAR ---
        aba_filtrar = QtWidgets.QWidget()
        lay_filtrar = QtWidgets.QVBoxLayout(aba_filtrar)

        lay_filtrar.addWidget(QtWidgets.QLabel("<b>FILTROS DICOM</b>"))

        lay_filtrar.addSpacing(10)
        lay_filtrar.addWidget(QtWidgets.QLabel("Threshold (HU):"))
        self.slider_hu = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_hu.setRange(-1000, 3000)
        self.slider_hu.setValue(200)  # Valor padrão para osso
        lay_filtrar.addWidget(self.slider_hu)

        # Labels indicativas de densidade
        lbl_hint = QtWidgets.QLabel("Osso: +200 a +1000 HU\nAr: -1000 HU")
        lbl_hint.setStyleSheet("color: #666; font-size: 9px;")
        lay_filtrar.addWidget(lbl_hint)

        lay_filtrar.addStretch()
        self.tabs.addTab(aba_filtrar, "⚖️ Filtrar")

        # Adicionamos as abas ao layout principal
        layout_principal.addWidget(self.tabs)

        # Botão de Conclusão fixo no final (fora das abas)
        btn_concluir = QtWidgets.QPushButton("Finalizar Etapa")
        btn_concluir.setStyleSheet("font-weight: bold; padding: 8px;")
        btn_concluir.clicked.connect(self._on_conclude_clicked)
        layout_principal.addWidget(btn_concluir)

        return toolbox_principal

    def validar_passagem(self) -> bool:
        return self._is_initialized

    def _on_conclude_clicked(self) -> None:
        if self.validar_passagem():
            self.concluido.emit()
        else:
            QtWidgets.QMessageBox.warning(None, "Aviso", "Ação obrigatória pendente.")