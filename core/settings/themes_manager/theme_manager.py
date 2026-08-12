from PySide6 import QtWidgets
from core.settings.paths.list_paths import THEMES_DIR
from core.settings.settings_app_manager import settings


class ThemeManager:
    """Gerencia temas estáticos modulares e customizações dinâmicas."""

    def __init__(self, app: QtWidgets.QApplication):
        self.app = app

    def apply_static_theme(self, theme_name: str) -> bool:
        theme_dir = THEMES_DIR / theme_name
        if not theme_dir.exists():
            theme_dir = THEMES_DIR

        components_dir = theme_dir / "components" if (theme_dir / "components").exists() else THEMES_DIR
        component_files = ["base.qss", "buttons.qss", "scrollbar.qss", "workspace.qss", "cards.qss"]

        stylesheet_parts = []
        try:
            loaded_any = False
            for comp in component_files:
                comp_path = components_dir / comp
                if comp_path.exists():
                    with open(comp_path, "r", encoding="utf-8") as f:
                        stylesheet_parts.append(f.read())
                        loaded_any = True

            if not loaded_any:
                single_file_path = THEMES_DIR / f"{theme_name}.qss"
                if single_file_path.exists():
                    with open(single_file_path, "r", encoding="utf-8") as f:
                        stylesheet_parts.append(f.read())
                        loaded_any = True

            if loaded_any:
                self.app.setStyleSheet("\n".join(stylesheet_parts))
                settings.tema = theme_name
                return True

        except Exception as e:
            print(f"Erro ao carregar tema estático {theme_name}: {e}")

        return False

    def get_user_customizations(self) -> dict:
        default_theme = {
            "bg_main": "#282c34",
            "bg_secondary": "#21252b",
            "bg_input": "#1b1f23",
            "border_color": "#181a1f",
            "text_color": "#abb2bf",
            "accent_color": "#61afef",
        }

        stored_colors = settings.get("theme_customization", "colors", default_theme)
        if not isinstance(stored_colors, dict):
            return default_theme
        return {**default_theme, **stored_colors}

    def apply_custom_theme(self) -> bool:
        colors = self.get_user_customizations()
        template_path = THEMES_DIR / "templates" / "dynamic_template.qss"

        if not template_path.exists():
            return False

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()

            replacements = {
                "{bg_main}": colors["bg_main"],
                "{bg_secondary}": colors["bg_secondary"],
                "{bg_input}": colors["bg_input"],
                "{border_color}": colors["border_color"],
                "{text_color}": colors["text_color"],
                "{accent_color}": colors["accent_color"],
            }

            for token, value in replacements.items():
                content = content.replace(token, value)

            self.app.setStyleSheet(content)
            return True
        except Exception as e:
            print(f"Erro ao aplicar tema customizado: {e}")
            return False

    def save_custom_color(self, key: str, hex_value: str) -> None:
        colors = self.get_user_customizations()
        colors[key] = hex_value

        settings.set("theme_customization", "colors", colors)
        settings.save()
        self.apply_custom_theme()