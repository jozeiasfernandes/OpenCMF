from PySide6 import QtWidgets, QtCore

# Localization
from core.settings.localization.translator import tr

# Settings
from core.settings.settings_app_manager import settings

# Themes
from core.settings.themes.theme_manager import ThemeManager
from core.settings.paths.list_paths import THEMES_DIR


class TabAppearance(QtWidgets.QWidget):
    tema_alterado = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager(QtWidgets.QApplication.instance())
        self._setup_ui()
        self._load_themes()
        self.retranslate_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QtWidgets.QFormLayout()
        self.lbl_tema = QtWidgets.QLabel()
        self.combo_temas = QtWidgets.QComboBox()
        self.combo_temas.setMinimumHeight(35)
        self.combo_temas.currentIndexChanged.connect(self._on_theme_changed)

        form.addRow(self.lbl_tema, self.combo_temas)
        layout.addLayout(form)
        layout.addStretch()

    def _load_themes(self):
        self.combo_temas.blockSignals(True)
        self.combo_temas.clear()

        if not THEMES_DIR.exists():
            self.combo_temas.addItem(tr("configs.default_theme"), userData=None)
            self.combo_temas.blockSignals(False)
            return

        found_themes = set()

        # 1. Procura arquivos .qss soltos na raiz (ex: atom.qss)
        for qss in THEMES_DIR.glob("*.qss"):
            found_themes.add(qss.stem)

        # 2. Procura pastas de temas modulares válidas
        ignored_dirs = {"components", "templates"}
        for path in THEMES_DIR.iterdir():
            if path.is_dir() and path.name not in ignored_dirs:
                # Valida se a pasta realmente é um tema (contém arquivos .qss nela ou dentro de uma pasta components)
                has_qss = list(path.glob("*.qss")) or list(path.glob("components/*.qss"))
                if has_qss:
                    found_themes.add(path.name)

        # Adiciona ao combobox ordenado
        for theme_name in sorted(found_themes):
            display_name = theme_name.replace("_", " ").capitalize()
            self.combo_temas.addItem(display_name, theme_name)

        # Sincroniza com a configuração atual salva
        current_theme = getattr(settings, "tema", "atom")
        for i in range(self.combo_temas.count()):
            if current_theme.lower() == self.combo_temas.itemData(i):
                self.combo_temas.setCurrentIndex(i)
                break

        self.combo_temas.blockSignals(False)

    def retranslate_ui(self):
        self.lbl_tema.setText(f"{tr('configs.theme_label')}:")

    def _on_theme_changed(self):
        theme_stem = self.combo_temas.currentData()
        if theme_stem:
            success = self.theme_manager.apply_static_theme(theme_stem)
            if success:
                settings.tema = theme_stem  # Garante persistência idêntica à MainWindow
                self.tema_alterado.emit(theme_stem)