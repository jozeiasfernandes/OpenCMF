## Princípios: 
* O Gizmo deve ser um componente transversal.
* Gizmo não deve modificar diretamente a geometria.


    Gizmo
    ├── TranslateGizmo
    ├── RotateGizmo
    ├── ScaleGizmo
    └── TransformGizmo

    gizmo.set_target(object)
    gizmo.set_mode("TRANSLATE")


Visualmente:

           Z
           ↑
           │
           │
       ─── ● ─── X
          /
         /
        Y

Ele deveria produzir uma transformação:

    Gizmo
       ↓
    Transform
       ↓
    Object

Isso permite integrar posteriormente:
    
    Undo/Redo
    History
    Command System
    Constraints
    Measurements
    Simulation

Por exemplo:

    User moves Mandible
            ↓
    Gizmo
            ↓
    TransformCommand
            ↓
    Object.transform
            ↓
    Scene updated
            ↓
    History records command


## Fluxo 

                 USER
                   │
                   ▼
             Viewport.Input
                   │
              ┌────┴────┐
              ▼         ▼
          Picking     Gizmo
              │         │
              └────┬────┘
                   ▼
                 Scene
                   │
                   ▼
                Command
                   │
                   ▼
                History