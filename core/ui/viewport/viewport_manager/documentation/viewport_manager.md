ViewportManager
│
├── Viewport_3D
├── Viewport_Axial
├── Viewport_Coronal
└── Viewport_Sagittal

## Operações

1. viewport_manager.create_viewport(...)
2. viewport_manager.remove_viewport(...)
3. viewport_manager.set_layout(...)
4. viewport_manager.active_viewport(viewport)

## Layouts

Single
└── 3D

Quad
├── Axial
├── Sagittal
├── Coronal
└── 3D

Dual
├── 3D
└── MPR

## Fluxo

Mouse
│
▼
Viewport
│
▼
InteractionManager
│
▼
Picking
│
▼
Mandible selected
│
▼
Gizmo activated
│
▼
User drags X axis
│
▼
TransformCommand
│
▼
Mandible.transform
│
▼
Scene update
│
├── Renderer update
├── Measurement update
├── Guides update
└── History update

## Componentes

Sistema	                | Responsabilidade
________________________|__________________________________
Viewport	        | Área de visualização
ViewportManager         | Gerencia múltiplos viewports
Camera                  | Projeção e posicionamento
OrientationSystem	| Frontal, posterior, superior etc.
CoordinateSystem	| Coordenadas e transformações
GizmoSystem	        | Translate/Rotate/Scale
OverlayManager	        | Elementos sobrepostos
Ruler	                | Escala e distância visual
GuideSystem	        | Linhas, planos e referências
GridSystem	        | Grades de referência
MeasurementSystem	| Medições
SelectionSystem	        | Seleção/picking
InteractionSystem	| Mouse/teclado e manipulação
ViewportSettings	| Preferências de visualização

## Separar 3D e 2DViewport

    │
    ├── 3D Viewport
    │     ├── 3D Gizmo
    │     ├── 3D Guides
    │     ├── Axis
    │     └── Orientation
    │
    └── 2D Viewport
        ├── Ruler
        ├── Crosshair
        ├── Guides
        ├── Measurements
        └── Labels

Ambos implementam interfaces comuns:

    IOverlay
    IInteraction
    IGizmo
    IGuide

Isso permite que uma ferramenta de medição funcione tanto em uma janela 2D quanto em 3D.


## Papel de cada componente
1. ViewportManager → administra múltiplos viewports e layouts.
2. Viewport → representa uma área de visualização.
3. Camera → perspectiva, ortográfica, zoom, pan, rotação e presets.
4. Gizmos → Translate, Rotate, Scale e futuramente transformações avançadas.
5. Orientation → Frontal, Posterior, Superior, Inferior, Sagital, Coronal etc.
6. CoordinateSystem → World, Local, Patient e eventualmente sistemas anatômicos.
7. Guides → linhas, planos, eixos e referências clínicas.
8. Ruler → escala visual e medição baseada nas unidades do mundo.
9. Grid → grade espacial de referência.
10. Overlays → elementos informativos sobre a visualização.
11. Interaction → seleção, picking, mouse, teclado, drag, snapping etc.
    12. ViewportSettings → preferências de visualização.

                 VIEWPORT
                     │
           ┌─────────┴─────────┐
           │                   │
       VISUALIZAÇÃO         INTERAÇÃO
           │                   │
           ├─ Camera           ├─ Selection
           ├─ Orientation      ├─ Picking
           ├─ Gizmos           ├─ Drag
           ├─ Ruler            ├─ Gizmo Interaction
           ├─ Grid             └─ Measurement
           ├─ Guides
           └─ Overlays