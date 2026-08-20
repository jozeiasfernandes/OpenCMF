## Elementos da interface

1. Ruler
2. Axis
3. Grid
4. Crosshair
5. OrientationMarker
6. CoordinateIndicator
7. SelectionOutline
8. MeasurementLabel
9. GuideLine
10. Gizmo


Eles não devem ser tratados como objetos anatômicos da Scene.

    Scene
     ├── Skull
     ├── Maxilla
     └── Mandible
    
    Viewport Overlay
     ├── Ruler
     ├── XYZ Axis
     ├── Orientation
     └── Gizmo

## OverlayManager

    Viewport
       │
       └── OverlayManager
              │
              ├── Gizmo
              ├── Ruler
              ├── Orientation
              ├── CoordinateIndicator
              ├── Guides
              ├── Grid
              ├── Crosshair
              └── Measurements

Cada Viewport pode configurar:

    overlay_manager.enable("ruler")
    overlay_manager.enable("orientation")
    overlay_manager.enable("grid")
    overlay_manager.disable("gizmo")

Ou 

    viewport.overlays.ruler.visible = True
    viewport.overlays.grid.visible = False


## Configuração global
View → Overlays

☑ Gizmo
☑ Orientation Marker
☑ Coordinate System
☑ Ruler
☐ Grid
☑ Guides
☑ Crosshair
☑ Measurements

E também:
View → Camera
    
    ○ Perspective
    ● Orthographic