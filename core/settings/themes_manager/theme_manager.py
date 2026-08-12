from PySide6 import QtWidgets

# Settings
from core.settings.paths.list_paths import THEMES_DIR
from core.settings.settings_app_manager import settings


class ThemeManager:
    """
    Gerencia a aplicação de temas estáticos (divididos em múltiplos arquivos modulares)
    e customizações dinâmicas de cores na aplicação PySide6, integrado com o SettingsManager.
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

        stored_colors = settings.get("theme_customization", "colors", default_theme)
        if not isinstance(stored_colors, dict):
            return default_theme
        return {**default_theme, **stored_colors}

    def apply_static_theme(self, theme_name: str) -> bool:
        """
        Aplica um tema estático carregando a pasta do tema e concatenando
        todos os arquivos de componentes modulares (base.qss, buttons.qss, cards.qss, etc.).
        """
        # Suporta tanto caso os arquivos fiquem em uma subpasta do tema quanto direto no THEMES_DIR
        theme_dir = THEMES_DIR / theme_name

        # Se a pasta do tema não existir, tenta procurar os arquivos modularizados diretamente na raiz ou numa pasta padrão
        if not theme_dir.exists():
            theme_dir = THEMES_DIR  # fallback se os componentes estiverem direto em THEMES_DIR ou numa pasta "components"

        components_dir = theme_dir / "components" if (theme_dir / "components").exists() else THEMES_DIR

        # Lista de arquivos modulares esperados
        component_files = [
            "base.qss",
            "buttons.qss",
            "scrollbar.qss",
            "workspace.qss",
            "cards.qss"  # <--- Novo arquivo incluído aqui
        ]

        stylesheet_parts = []
        try:
            # Tenta carregar cada componente modular se ele existir
            loaded_any = False
            for comp in component_files:
                comp_path = components_dir / comp
                if comp_path.exists():
                    with open(comp_path, "r", encoding="utf-8") as f:
                        stylesheet_parts.append(f.read())
                        loaded_any = True

            # Fallback caso o tema seja apenas um único arquivo consolidado (ex: atom.qss antigo)
            if not loaded_any:
                single_file_path = THEMES_DIR / f"{theme_name}.qss"
                if single_file_path.exists():
                    with open(single_file_path, "r", encoding="utf-8") as f:
                        stylesheet_parts.append(f.read())
                        loaded_any = True

            if loaded_any:
                full_stylesheet = "\n".join(stylesheet_parts)
                self.app.setStyleSheet(full_stylesheet)
                settings.tema = theme_name
                return True
            else:
                print(f"Nenhum arquivo de estilo encontrado para o tema: {theme_name}")

        except Exception as e:
            print(f"Erro ao carregar o tema estático {theme_name}: {e}")

        return False

    def apply_custom_theme(self) -> bool:
        colors = self.get_user_customizations()
        template_path = THEMES_DIR / "templates" / "dynamic_template.qss"

        if not template_path.exists():
            return False

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            replacements = {
                "{bg_main}": colors["bg_main"],
                "{bg_secondary}": colors["bg_secondary"],
                "{bg_input}": colors["bg_input"],
                "{border_color}": colors["border_color"],
                "{text_color}": colors["text_color"],
                "{accent_color}": colors["accent_color"],
            }

            final_stylesheet = template_content
            for token, value in replacements.items():
                final_stylesheet = final_stylesheet.replace(token, value)

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