from PySide6 import QtWidgets, QtCore
from core.settings.localization.translator import tr
from core.settings.settings_app_manager import settings
from core.settings.themes.theme_manager import ThemeManager

from settings.paths.list_paths import THEMES_DIR


class TabAppearance(QtWidgets.QWidget):
    tema_alterado = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Inicializa o ThemeManager passando a instância global do app
        self.theme_manager = ThemeManager(QtWidgets.QApplication.instance())
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
        themes_dir = THEMES_DIR

        self.combo_temas.blockSignals(True)
        if not themes_dir.exists():
            self.combo_temas.addItem(tr("configs.default_theme"), userData=None)
            self.combo_temas.blockSignals(False)
            return

        for qss in themes_dir.glob("*.qss"):
            # Salvamos o stem (ex: 'atom', 'claro') como dado para facilitar o uso no ThemeManager
            self.combo_temas.addItem(qss.stem.replace("_", " ").capitalize(), qss.stem)

        # Sincroniza com a configuração salva no settings
        current_theme = settings.get("preferencias", "tema", "atom")
        for i in range(self.combo_temas.count()):
            if current_theme.lower() == self.combo_temas.itemData(i):
                self.combo_temas.setCurrentIndex(i)
                break
        self.combo_temas.blockSignals(False)

    def retranslate_ui(self):
        self.lbl_tema.setText(f"{tr('configs.theme_label')}:")

    def _on_tema_changed(self):
        theme_stem = self.combo_temas.currentData()
        if theme_stem:
            # Aplica e salva o tema estático utilizando o ThemeManager
            success = self.theme_manager.apply_static_theme(theme_stem)
            if success:
                # Emite o sinal caso algum componente externo precise escutar a mudança
                self.tema_alterado.emit(theme_stem)