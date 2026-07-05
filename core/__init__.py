# core/__init__.py
from .home_page.settings_app import settings
from .icons.icons_manager import IconManager
from .localization.translator import tr

# Expondo gerenciadores comuns
from .home_page.managers.project_service_home_page import ProjectServiceHomePage
from .home_page.managers.flow_service_home_page import FlowServiceHomePage