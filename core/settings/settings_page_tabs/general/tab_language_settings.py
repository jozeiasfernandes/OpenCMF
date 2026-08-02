import json
from PySide6 import QtWidgets, QtCore
from core.settings.localization.translator import tr
from settings.settings_app_manager import settings

from list_paths import TRANSLATIONS_DIR


class TabLanguage(QtWidgets.QWidget):
    idioma_alterado = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self._bloquear_aviso = True
        self._setup_ui()
        self._carregar_idiomas_disponiveis()
        self._sincronizar_combo()
        self.retranslate_ui()
        self._bloquear_aviso = False

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QtWidgets.QFormLayout()
        self.lbl_lang = QtWidgets.QLabel()
        self.combo_idioma = QtWidgets.QComboBox()
        self.combo_idioma.setMinimumHeight(35)
        self.combo_idioma.currentIndexChanged.connect(self._on_idioma_changed)

        form.addRow(self.lbl_lang, self.combo_idioma)
        layout.addLayout(form)
        layout.addStretch()

    def _carregar_idiomas_disponiveis(self):
        # Utiliza o TRANSLATIONS_DIR centralizado do list_paths
        trans_dir = TRANSLATIONS_DIR

        self.combo_idioma.blockSignals(True)
        self.combo_idioma.clear()

        if trans_dir.exists():
            for file in trans_dir.glob("*.json"):
                lang_code = file.stem
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        display_name = data.get("meta", {}).get("language_name", lang_code)
                except Exception:
                    display_name = lang_code
                self.combo_idioma.addItem(display_name, lang_code)
        else:
            print(f"Diretório de traduções não encontrado: {trans_dir}")

        self.combo_idioma.blockSignals(False)

    def _sincronizar_combo(self):
        current_lang = settings.get("preferencias", "idioma", "pt_BR")
        index = self.combo_idioma.findData(current_lang)
        if index >= 0:
            self.combo_idioma.setCurrentIndex(index)

    def retranslate_ui(self):
        self.lbl_lang.setText(f"{tr('configs.language_label')}:")

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