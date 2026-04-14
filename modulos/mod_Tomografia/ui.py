# ui.py - Isolar toda a construção da interface (widgets, botões, sliders e layouts)

from PySide6 import QtWidgets, QtCore
from typing import Dict, Callable


class TomografiaUI:
    def __init__(self):
        self.edit_dicom = QtWidgets.QLineEdit()
        self.btn_validar = QtWidgets.QPushButton("🔍 Validar DICOM")
        self.btn_carregar = QtWidgets.QPushButton("⌛ Carregar DICOM")
        self.btn_finalizar = QtWidgets.QPushButton("Finalizar Etapa")

        self.slider_hu = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sliders_navegacao: Dict[str, QtWidgets.QSlider] = {}
        self.layout_filtros = None

    def setup_toolboxes(self,
                        on_buscar: Callable,
                        on_validar: Callable,
                        on_carregar: Callable,
                        on_threshold: Callable,
                        on_finalizar: Callable) -> Dict[str, QtWidgets.QWidget]:

        return {
            "Abrir": self._create_aba_abrir(on_buscar, on_validar, on_carregar, on_finalizar),
            "Filtrar": self._create_aba_filtrar(on_threshold)
        }

    def _create_aba_abrir(self, on_buscar, on_validar, on_carregar, on_finalizar) -> QtWidgets.QWidget:
        aba = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(aba)

        layout.addWidget(QtWidgets.QLabel("<b>GESTÃO DE ARQUIVOS</b>"))

        # Linha de Seleção de Pasta
        form = QtWidgets.QFormLayout()
        linha_busca = QtWidgets.QWidget()
        h_lay = QtWidgets.QHBoxLayout(linha_busca)
        h_lay.setContentsMargins(0, 0, 0, 0)

        btn_pasta = QtWidgets.QPushButton("...")
        btn_pasta.setFixedWidth(30)
        btn_pasta.clicked.connect(on_buscar)

        h_lay.addWidget(self.edit_dicom)
        h_lay.addWidget(btn_pasta)
        form.addRow("Pasta:", linha_busca)
        layout.addLayout(form)

        # Botões de Ação
        self.btn_validar.clicked.connect(on_validar)
        layout.addWidget(self.btn_validar)

        self.btn_carregar.setEnabled(False)
        self.btn_carregar.setStyleSheet("font-weight: bold; background-color: #2980b9; color: white;")
        self.btn_carregar.clicked.connect(on_carregar)
        layout.addWidget(self.btn_carregar)

        layout.addStretch()

        self.btn_finalizar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_finalizar.clicked.connect(on_finalizar)
        layout.addWidget(self.btn_finalizar)

        return aba

    def _create_aba_filtrar(self, on_threshold) -> QtWidgets.QWidget:
        aba = QtWidgets.QWidget()
        self.layout_filtros = QtWidgets.QVBoxLayout(aba)

        self.layout_filtros.addWidget(QtWidgets.QLabel("<b>FILTROS E NAVEGAÇÃO</b>"))

        self.slider_hu.setRange(-1000, 3000)
        self.slider_hu.setValue(200)
        self.slider_hu.valueChanged.connect(on_threshold)

        self.layout_filtros.addWidget(QtWidgets.QLabel("Threshold 3D (HU):"))
        self.layout_filtros.addWidget(self.slider_hu)

        self.layout_filtros.addStretch()
        return aba

    def update_status_validado(self):
        self.btn_validar.setText("✅ DICOM Validado")
        self.btn_validar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_carregar.setEnabled(True)

    def update_status_erro(self):
        self.btn_validar.setText("❌ Erro na Pasta")
        self.btn_validar.setStyleSheet("background-color: #c0392b; color: white;")

    def update_status_carregado(self):
        self.btn_carregar.setText("✅ Carregamento concluído")
        self.btn_carregar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")

    def setup_navigation_sliders(self, info_planos: Dict[str, int], on_scroll_sync: Callable):
        """Cria sliders dinâmicos para Axial, Sagital e Coronal."""
        # Limpa sliders existentes
        for s in self.sliders_navegacao.values():
            s.parent().deleteLater()
        self.sliders_navegacao.clear()

        for plano, total in info_planos.items():
            container = QtWidgets.QWidget()
            v_lay = QtWidgets.QVBoxLayout(container)
            v_lay.setContentsMargins(0, 5, 0, 5)

            label = QtWidgets.QLabel(f"Navegação {plano}:")
            slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            slider.setRange(0, total - 1)
            slider.setValue(total // 2)
            slider.valueChanged.connect(lambda v, p=plano: on_scroll_sync(p, v))

            v_lay.addWidget(label)
            v_lay.addWidget(slider)

            self.layout_filtros.insertWidget(1, container)
            self.sliders_navegacao[plano] = slider

            self.layout_filtros.update()
            if self.layout_filtros.parentWidget():
                self.layout_filtros.parentWidget().repaint()