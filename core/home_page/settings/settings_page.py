import json
import sys
from pathlib import Path
from PySide6 import QtWidgets, QtCore

from core.localization.translator import tr
from core.home_page.settings_app import settings


class PaginaConfig(QtWidgets.QWidget):
    voltar_solicitado = QtCore.Signal()
    tema_alterado = QtCore.Signal(str)
    idioma_alterado = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self._bloquear_aviso = True
        self._setup_ui()
        self._carregar_idiomas_disponiveis()
        self._sincronizar_combos()
        self.retranslate_ui()
        self._bloquear_aviso = False

    def _setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(50, 50, 50, 50)
        self.main_layout.setSpacing(30)

        self.lbl_title = QtWidgets.QLabel()
        self.main_layout.addWidget(self.lbl_title, alignment=QtCore.Qt.AlignTop)

        form_container = QtWidgets.QFormLayout()
        form_container.setSpacing(20)

        self.combo_temas = QtWidgets.QComboBox()
        self.combo_temas.setMinimumHeight(35)
        self._carregar_temas()
        self.combo_temas.currentIndexChanged.connect(self._on_tema_changed)

        self.combo_idioma = QtWidgets.QComboBox()
        self.combo_idioma.setMinimumHeight(35)
        self.combo_idioma.currentIndexChanged.connect(self._on_idioma_changed)

        self.lbl_tema = QtWidgets.QLabel()
        self.lbl_lang = QtWidgets.QLabel()

        form_container.addRow(self.lbl_tema, self.combo_temas)
        form_container.addRow(self.lbl_lang, self.combo_idioma)
        self.main_layout.addLayout(form_container)
        self.main_layout.addStretch()

        self.btn_fechar = QtWidgets.QPushButton()
        self.btn_fechar.setFixedSize(150, 45)
        self.btn_fechar.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_fechar.setObjectName("btn_fechar_config")
        self.btn_fechar.clicked.connect(self.voltar_solicitado.emit)
        self.main_layout.addWidget(self.btn_fechar, alignment=QtCore.Qt.AlignCenter)

    def _carregar_idiomas_disponiveis(self):
        base_path = Path(__file__).resolve().parents[3]
        trans_dir = base_path / "core" / "localization" / "translations"
        self.combo_idioma.blockSignals(True)

        for file in trans_dir.glob("*.json"):
            lang_code = file.stem
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    display_name = data.get("meta", {}).get("language_name", lang_code)
            except:
                display_name = lang_code

            self.combo_idioma.addItem(display_name, lang_code)

        self.combo_idioma.blockSignals(False)

    def retranslate_ui(self):
        self.lbl_title.setText(f"<h2>{tr('configs.settings_title')}</h2>")
        self.lbl_tema.setText(f"{tr('configs.theme_label')}:")
        self.lbl_lang.setText(f"{tr('configs.language_label')}:")
        self.btn_fechar.setText(tr("common.close_button"))

    def _sincronizar_combos(self):
        current_lang = settings.get("preferencias", "idioma", "pt_BR")
        index = self.combo_idioma.findData(current_lang)
        if index >= 0:
            self.combo_idioma.setCurrentIndex(index)

    def _carregar_temas(self):
        themes_dir = Path(__file__).resolve().parents[3] / "appearance" / "themes"
        if not themes_dir.exists():
            self.combo_temas.addItem(tr("configs.default_theme"), userData=None)
            return

        self.combo_temas.blockSignals(True)
        for qss in themes_dir.glob("*.qss"):
            self.combo_temas.addItem(qss.stem.replace("_", " ").capitalize(), str(qss))

        current_theme = settings.get("preferencias", "tema", "dark")
        for i in range(self.combo_temas.count()):
            if current_theme in self.combo_temas.itemText(i).lower():
                self.combo_temas.setCurrentIndex(i)
                break
        self.combo_temas.blockSignals(False)

    def _on_tema_changed(self):
        if path_qss := self.combo_temas.currentData():
            self.tema_alterado.emit(path_qss)

    def _on_idioma_changed(self):
        if self._bloquear_aviso:
            return

        lang_code = self.combo_idioma.currentData()
        settings.set("preferencias", "idioma", lang_code)
        settings.save()

        QtWidgets.QMessageBox.information(
            self,
            tr("configs.language_changed_title"),
            tr("configs.restart_required_msg")
        )
        self.idioma_alterado.emit(lang_code)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    config_page = PaginaConfig()
    window.setCentralWidget(config_page)
    window.show()
    sys.exit(app.exec())