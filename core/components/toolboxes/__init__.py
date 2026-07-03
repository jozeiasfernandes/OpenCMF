# core/components/toolboxes/__init__.py
from .object_manager_toolbox import ObjetoManagerWidget
from .registration_toolbox import Component as RegistrationToolbox
from .object_manager_toolbox_02 import ObjetoManagerWidget
from .segmentation_toolbox import Component as SegmentationToolbox
from .scene_toolbox import Component as SceneToolbox
from .objetct_properties_toolbox import Component as PropertiesComponent


__all__ = ["ObjetoManagerWidget", "RegistrationToolbox", "ObjetoManagerWidget", "SegmentationToolbox", "SceneToolbox", "PropertiesComponent"]