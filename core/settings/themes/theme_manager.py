from PySide6 import QtWidgets
from settings.paths.list_paths import THEMES_DIR
from core.settings.settings_app_manager import settings


class ThemeManager:
    """
    Gerencia a aplicação de temas estáticos e customizações dinâmicas
    de cores na aplicação PySide6, integrado com o SettingsManager.
    """

    def __init__(self, app: QtWidgets.QApplication):
        self.app = app

    def get_user_customizations(self) -> dict:
        """
        Retorna as cores customizadas salvas via SettingsManager ou um tema padrão (Atom Dark).
        """
        default_theme = {
            "bg_main": "#282c34",
            "bg_secondary": "#21252b",
            "bg_input": "#1b1f23",
            "border_color": "#181a1f",
            "text_color": "#abb2bf",
            "accent_color": "#61afef",
        }

        # Busca customizações na categoria 'theme_customization' gerenciada pelo SettingsManager
        return settings.get("theme_customization", "colors", default_theme)

    def apply_static_theme(self, theme_name: str) -> bool:
        """
        Aplica um arquivo de tema estático completo (ex: atom.qss, claro.qss)
        e atualiza a preferência no SettingsManager.
        """
        theme_path = THEMES_DIR / f"{theme_name}.qss"
        if theme_path.exists():
            try:
                with open(theme_path, "r", encoding="utf-8") as f:
                    stylesheet = f.read()
                    self.app.setStyleSheet(stylesheet)
                    settings.tema = theme_name
                    return True
            except Exception as e:
                print(f"Erro ao carregar o tema estático {theme_name}: {e}")
        return False

    def apply_custom_theme(self) -> bool:
        """
        Lê o template dinâmico QSS, injeta as cores customizadas e aplica no app.
        """
        colors = self.get_user_customizations()
        template_path = THEMES_DIR / "templates" / "dynamic_template.qss"

        if not template_path.exists():
            return False

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            final_stylesheet = template_content.format(**colors)
            self.app.setStyleSheet(final_stylesheet)
            return True
        except Exception as e:
            print(f"Erro ao aplicar o tema customizado: {e}")
            return False

    def save_custom_color(self, key: str, hex_value: str) -> None:
        """
        Altera uma cor específica da customização em tempo de execução,
        salva usando o SettingsManager e reaplica o tema instantaneamente.
        """
        current_colors = self.get_user_customizations()
        current_colors[key] = hex_value

        settings.set("theme_customization", "colors", current_colors)
        settings.save()

        self.apply_custom_theme()