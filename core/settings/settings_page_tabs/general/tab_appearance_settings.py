from PySide6 import QtWidgets, QtCore
from settings.localization.translator import tr
from settings.settings_app_manager import settings

from list_paths import THEMES_DIR


class TabAppearance(QtWidgets.QWidget):
    tema_alterado = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._carregar_temas()
        self.retranslate_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QtWidgets.QFormLayout()
        self.lbl_tema = QtWidgets.QLabel()
        self.combo_temas = QtWidgets.QComboBox()
        self.combo_temas.setMinimumHeight(35)
        self.combo_temas.currentIndexChanged.connect(self._on_tema_changed)

        form.addRow(self.lbl_tema, self.combo_temas)
        layout.addLayout(form)
        layout.addStretch()

    def _carregar_temas(self):
        # Utiliza o THEMES_DIR centralizado do list_paths
        themes_dir = THEMES_DIR

        self.combo_temas.blockSignals(True)
        if not themes_dir.exists():
            self.combo_temas.addItem(tr("configs.default_theme"), userData=None)
            self.combo_temas.blockSignals(False)
            return

        for qss in themes_dir.glob("*.qss"):
            self.combo_temas.addItem(qss.stem.replace("_", " ").capitalize(), str(qss))

        # Sincroniza com a configuração salva
        current_theme = settings.get("preferencias", "tema", "dark")
        for i in range(self.combo_temas.count()):
            if current_theme in self.combo_temas.itemText(i).lower():
                self.combo_temas.setCurrentIndex(i)
                break
        self.combo_temas.blockSignals(False)

    def retranslate_ui(self):
        self.lbl_tema.setText(f"{tr('configs.theme_label')}:")

    def _on_tema_changed(self):
        path_qss = self.combo_temas.currentData()
        if path_qss:
            # Salva a preferência
            theme_name = self.combo_temas.currentText().lower()
            settings.set("preferencias", "tema", theme_name)
            settings.save()

            # Emite o sinal para que a aplicação principal aplique o novo QSS
            self.tema_alterado.emit(path_qss)