from typing import Dict, Any, Callable
from core.components.central_area.viewer_2d_central_area import Viewer2D_Widget_CentralArea
from core.components.central_area.viewer_3d_dicom_central_area import Viewer3D_Dicom_Widget_CentralArea
from domain.volume.visualization.volume_viewer.constants import VolumeViewerConstants


class VolumeViewerFactory:
    @staticmethod
    def create_viewers(
            context: Any,
            event_bus: Any,
            registry: Any,
            callbacks: Dict[str, Callable]
    ) -> Dict[str, Any]:

        vistas: Dict[str, Any] = {}
        safe_context = context if context is not None else callbacks.get('self_ref')

        # 1. 2D Viewers (Axial, Sagittal, Coronal)
        for name in VolumeViewerConstants.PLANES:
            pane = Viewer2D_Widget_CentralArea(
                context=safe_context,
                title=name,
                cor=VolumeViewerConstants.COLORS[name]
            )

            # 2D viewer signal connections (using default argument binding to prevent lambda capture issues)
            pane.sliceChanged.connect(lambda v, n=name: callbacks['on_slice_changed'](n, v))
            pane.maximizeRequested.connect(lambda m, n=name: callbacks['on_maximize'](n, m))

            if hasattr(pane, 'lutChanged'):
                pane.lutChanged.connect(callbacks['on_lut_changed'])

            vistas[name] = pane

        # 2. 3D Viewer
        p3d = Viewer3D_Dicom_Widget_CentralArea(
            context=safe_context,
            title="3D",
            cor=VolumeViewerConstants.COLORS["3D"],
            event_bus=event_bus,
            viewer_registry=registry
        )

        # 3D viewer signal connections
        if hasattr(p3d, 'thresholdChanged'):
            p3d.thresholdChanged.connect(callbacks['on_threshold_changed'])

        if hasattr(p3d, 'viewChanged'):
            p3d.viewChanged.connect(callbacks['on_3d_view_changed'])

        if hasattr(p3d, 'presetChanged'):
            p3d.presetChanged.connect(callbacks['on_preset_changed'])

        p3d.maximizeRequested.connect(lambda m: callbacks['on_maximize']("3D", m))

        vistas["3D"] = p3d
        return vistas